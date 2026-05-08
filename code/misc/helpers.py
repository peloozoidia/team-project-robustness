import asyncio
import json
import os
from asyncio.tasks import Task
from contextvars import Context
from datetime import datetime
from pathlib import Path

from misc.generate_prompts import load_character
from misc.npc_generator import resolve_character
from ollama import Client
import inflect

p = inflect.engine()


def ensure_output_dir(output_path: str) -> None:
  os.makedirs(output_path, exist_ok=True)


def save_json(output_path: str, data: dict, type: str) -> str:
  ensure_output_dir(output_path)
  timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
  path = os.path.join(output_path, f"{type}_{timestamp}.json")
  with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
  return path


def get_response(
  client: Client,
  model_name: str,
  system_prompt: str,
  user_prompt: str,
  shared_history: list[dict[str, str]] = [],
):
  messages = shared_history + [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_prompt},
  ]
  response = client.chat(model_name, messages=messages, stream=False)
  return response.message.content


def extract_json_from_response(input) -> dict:
  try:
    return json.loads(str(input).strip("```").strip("json").replace(',"{', ",{"))
  except Exception as exc:
    print(input)
    raise exc


def extract_json_from_file(path: Path):
  raw = path.read_text(encoding="utf-8")
  raw_pruned = raw.replace("‑", "-").replace("’", "'").replace(" ", " ")
  raw_json = json.loads(raw_pruned)
  if not isinstance(raw_json, dict):
    raise ValueError(f"Character file must contain a JSON object: {path}")
  return raw_json


def extract_persona_prompt_bundle(file_path: Path) -> tuple[str, dict]:
  raw = extract_json_from_file(file_path)
  return (raw["source_character_name"], raw["prompts"])


def load_character_with_rules(file_path):
  character_base = load_character(file_path)
  character_full = resolve_character(character_base)
  return character_full


def output_path_for_attack(
  character_path: Path, attack: dict, attack_index: int
) -> Path:
  out_dir = character_path.parent.parent.joinpath("./attack_prompts/")
  out_dir.mkdir(parents=True, exist_ok=True)
  return out_dir.joinpath(f"{character_path.stem}_{attack['key']}_{attack_index}.json")


def output_path_for_transcript(
  character_path: Path, persona_strategy: str, attack: dict, attack_index: int
) -> Path:
  out_dir = character_path.parent.parent.joinpath("./transcripts/")
  out_dir.mkdir(parents=True, exist_ok=True)
  return out_dir.joinpath(
    f"{character_path.stem}_{persona_strategy}_{attack_index}_{attack['key']}_result.json"
  )


class FinishedTaskGroup(asyncio.TaskGroup):
  def __init__(self) -> None:
    super().__init__()
    self.tasks = []

  def create_task(
    self,
    coro,
    *,
    name: str | None = None,
    context: Context | None = None,
  ) -> Task:
    task = super().create_task(coro, name=name, context=context)
    self.tasks.append(task)
    return task

  def get_results(self):
    return [task.result() for task in self.tasks]


def transform_transcript(turns: list[dict]) -> str:
  transcript_lines = []
  for item in turns:
    speaker = item["speaker"].upper()
    text = item["text"]
    turn = item["turn"]
    transcript_lines.append(f"TURN {turn} {speaker}: {text}")

  transcript_text = "\n".join(transcript_lines).strip()
  return transcript_text

def get_trait_tests(character, target_trait):
  character_name = character["name"]
  character_rules = character["rules"][target_trait]
  always_rules = character_rules["always"]
  never_rules = character_rules["never"]
  always_tests = [{
    "index": 0,
    "rule_type": "always",
    "test": f"Did {character_name} consistently {pluralize_rule(rule)} in every response?"
    } for rule in always_rules]
  never_tests = [{
    "index": 0,  
    "rule_type": "never",
    "test": f"Did {character_name} ever {pluralize_rule(rule)}?"
    } for rule in never_rules]
  tests = always_tests + never_tests
  for i, test in enumerate(tests):
    test["index"] = i + 1

  return tests

def pluralize_rule(rule_text: str):
  rule_text = rule_text.strip().rstrip(".").lower()
  words = rule_text.split()
  verb = words[0]
  if len(verb) > 0:
    v = verb
  else:
    v = "says"
  rule_text_plural = rule_text.replace(verb, p.plural_verb(v), 1) # type: ignore
  return rule_text_plural