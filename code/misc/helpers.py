from asyncio.tasks import Task
from contextvars import Context
from datetime import datetime
import json
from pathlib import Path
from ollama import Client
import os
from misc.generate_prompts import load_character
from npc_generator import resolve_character
import asyncio


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


def extract_prompt_bundle_from_response(input) -> dict:
  return json.loads(str(input).strip("```").strip("json"))

def extract_persona_prompt_bundle(file_path: Path) -> dict:
  raw = json.loads(file_path.read_text(encoding="utf-8"))
  if not isinstance(raw, dict):
    raise ValueError(f"Character file must contain a JSON object: {file_path}")
  return raw["prompts"]


def load_character_with_rules(file_path):
  character_base = load_character(file_path)
  character_full = resolve_character(character_base)
  return character_full


def output_path_for_attack(
  character_path: Path, attack: dict, attack_index: int
) -> Path:
  out_dir = character_path.parent.parent.joinpath("./attack_prompts/")
  out_dir.mkdir(parents=True, exist_ok=True)
  return out_dir.joinpath(
    f"{character_path.stem}_{attack['key']}_{attack_index}.json"
  )

def output_path_for_transcript(
  character_path: Path, persona_strategy: str, attack: dict, attack_index: int
) -> Path:
  out_dir = character_path.parent.parent.joinpath("./transcripts/")
  out_dir.mkdir(parents=True, exist_ok=True)
  return out_dir.joinpath(
    f"{character_path.stem}_{persona_strategy}_{attack['key']}_{attack_index}_result.json"
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
