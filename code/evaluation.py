import json
import os
import sys
from pathlib import Path

import config
import jsonschema
from assets.evaluating_llm import (
  SYSTEM_PROMPT,
  evaluation_result_schema,
  get_task_prompt,
)
from misc.helpers import (
  extract_json_from_response,
  load_character_with_rules,
  save_json,
  transform_transcript,
)
from misc.llm_client import LLMClient


def main() -> int:
  character_dir = Path(config.OUTPUT_PATH).joinpath("./characters")
  transcript_dir = Path(config.OUTPUT_PATH).joinpath("./transcripts")
  output_dir = Path(config.OUTPUT_PATH).joinpath("./results")

  character_files = [
    character_dir.joinpath(character)
    for character in os.listdir(character_dir)
    if character.endswith(".json")
  ]

  results: list[dict] = []

  for character_path in character_files:
    character = load_character_with_rules(character_path)

    transcript_files = [
      transcript_dir.joinpath(file)
      for file in os.listdir(transcript_dir)
      if file.startswith(character_path.stem)
    ]
    transcripts = [
      json.loads(file.read_text(encoding="utf-8")) for file in transcript_files
    ]

    for attack_transcript in transcripts:
      try:
        test_results = get_test_results(character, attack_transcript)
        test_score = sum([test["result"] for test in test_results["test_results"]])

        # temporarily extract strategy, future just use attack_transcript["persona_prompt_strategy"]
        prompt_strategy = str(attack_transcript["persona_system_prompt"]).split("]", maxsplit=2)[0].lstrip("[STRATEGY: ]")
        data = {
          "character": character["name"],
          "persona_key": prompt_strategy,
          "persona_llm": attack_transcript["persona_llm"],
          "attack_key": attack_transcript["attack_prompts"]["attack"]["key"],
          "attack_id": f"{attack_transcript["attack_prompts"]["attack"]["key"]}_{attack_transcript["attack_prompts"]["index"]}",
          "attacker_llm": attack_transcript["attacker_llm"],
          "test_score": test_score,
          "test_results": test_results["test_results"],
        }
        results.append(data)
      except Exception as exc:
        print(f"Failed to generate test tesults: {exc}", file=sys.stderr)
        return 1

  output_path = save_json(output_dir.__str__(), {"results": results}, "eval_result")
  print(f"Saved transcript evaluation results to {output_path}")
  return 0


def get_test_results(persona, transcript) -> dict[str, list]:
  llm = LLMClient(config.EVALUATING_LLM)
  transcript_text = transform_transcript(transcript["transcript"])
  try:
    response = llm.chat(
      SYSTEM_PROMPT,
      get_task_prompt(
        persona, transcript_text, transcript["attack_prompts"]["test_prompts"]
      ),
    )
    response_json = extract_json_from_response(response)
    try:
      jsonschema.validate(response_json, evaluation_result_schema)
      return response_json
    except Exception as exc:
      raise Exception(f"Validation error: {exc}")
  except Exception as exc:
    raise Exception(f"LLM Response error: {exc}")


main()
