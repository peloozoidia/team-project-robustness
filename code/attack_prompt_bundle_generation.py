import asyncio
import json
import os
import sys
import time
import uuid
from pathlib import Path

import config
import jsonschema
from assets.attack_generating_llm import (
  SYSTEM_PROMPT,
  get_attack_bundle_schema,
  get_task_prompt,
)
from assets.attacks import attack_schema, get_test_collection
from misc.helpers import (
  extract_json_from_response,
  load_character_with_rules,
  output_path_for_attack,
)
from misc.llm_client import LLMClient


async def generate_attacks_for_persona_and_attack(
  character_path, persona, attack, semaphore
) -> int:
  async with semaphore:
    llm = LLMClient(config.ATTACK_GENERATING_LLM)
    try:
      try:
        jsonschema.validate(attack, attack_schema)
      except Exception as exc:
        print(f"Failed to validate attack object: {exc}", file=sys.stderr)
        return 1

      response = await llm.asyncChat(
        SYSTEM_PROMPT,
        get_task_prompt(
          persona, attack
        ),
      )
      response_json = extract_json_from_response(response)
      try:
        jsonschema.validate(
          response_json,
          get_attack_bundle_schema(),
        )  # validate to ensure LLM response is in the right schema
      except Exception as exc:
        print(f"Failed to validate LLM response: {exc}", file=sys.stderr)
        return 1

      # saving each attack in a separate file for easier dialogue generation
      for prompts in response_json["bundle"]:
        data = {
          "attack_set_id": str(uuid.uuid4()),
          "attack": attack,
          "index": prompts["index"],
          "target_trait": prompts["target_trait"],
          "system_prompt": prompts["system_prompt"],
          "starting_prompt": prompts["starting_prompt"],
          "task_prompt": prompts["task_prompt"],
          "test_prompts": prompts["test_prompts"],
        }
        out_path = output_path_for_attack(character_path, attack, data["index"])
        out_path.write_text(
          json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    except Exception as exc:
      print(
        f"Failed to generate prompts for {persona['name']}, attack {attack['key']}: {exc}",
        file=sys.stderr,
      )
      return 1

    return 0


async def main() -> int:
  start = time.perf_counter()

  directory_path = Path(config.OUTPUT_PATH).joinpath("./characters")

  character_files = [
    directory_path.joinpath(character)
    for character in os.listdir(directory_path)
    if character.endswith(".json")
  ]

  attacks = get_test_collection(config.GENERATED_ATTACKS_COUNT)

  semaphore = asyncio.Semaphore(config.MAX_CONCURRENT_REQUESTS)
  calls = []
  for character_path in character_files:
    character = load_character_with_rules(character_path)
    generations = [
      generate_attacks_for_persona_and_attack(
        character_path, character, attack, semaphore
      )
      for attack in attacks
    ]
    calls.extend(generations)

  results = await asyncio.gather(*calls, return_exceptions=True)

  successful = sum(1 for result in results if isinstance(result, int) and result == 0)
  print(
    f"Successfully generated {successful} attack prompt bundles for {len(character_files)} characters and {len(attacks)} attacks."
  )

  errors = [result for result in results if (isinstance(result, int) and result != 0)]
  if errors:
    print(f"Encountered {len(errors)} errors during generation.")

  end = time.perf_counter()
  print(f"Attack prompt bundle generation completed in {end - start:.2f} seconds.")
  return 0


asyncio.run(main())
