import asyncio
import itertools as itools
import json
import os
import sys
import time
import uuid
from pathlib import Path

import config
from assets.attack_generating_llm import (
  SYSTEM_PROMPT,
  get_task_prompt,
)
from assets.attacks import get_test_collection
from misc.helpers import (
  extract_json_from_file,
  load_character_with_rules,
  output_path_for_attack,
)
from misc.llm_client import LLMClient
from misc.structured_pydantic_output import Attack, AttackBundle


async def generate_attacks_for_persona_and_attack(
  character_path, persona, attack, semaphore
) -> int:
  async with semaphore:
    llm = LLMClient(config.ATTACK_GENERATING_LLM)
    try:
      try:
        Attack.model_validate(attack)
      except Exception as exc:
        print(f"Failed to validate attack object: {exc}", file=sys.stderr)
        return 1

      try:
        response = await llm.asyncChat(
          SYSTEM_PROMPT,
          get_task_prompt(persona, attack),
          format=AttackBundle,
        )

      except Exception as exc:
        print(f"LLM call failed: {exc}", file=sys.stderr)
        return 1
      try:
        bundle = AttackBundle.model_validate_json(json_data=response)
      except Exception as exc:
        print(f"LLM response validation error: {exc}", file=sys.stderr)
        return 1

      # saving each attack in a separate file for easier dialogue generation
      for prompts in bundle.bundle:
        data = {
          "attack_set_id": str(uuid.uuid4()),
          "attack": attack,
          "index": prompts.index,
          "target_trait": prompts.target_trait,
          "system_prompt": prompts.system_prompt,
          "starting_prompt": prompts.starting_prompt,
          "task_prompt": prompts.task_prompt,
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

  combinations = list(itools.product(character_files, attacks))
  total_combinations = len(combinations)

  checkpoint_path = Path.cwd().joinpath("pipeline/checkpoint-attack-bundles.json")
  checkpoint = extract_json_from_file(checkpoint_path)
  next_combination_index = int(checkpoint["next_combination_index"])
  if next_combination_index >= total_combinations:
    print("All combinations have already been processed.")
    return 0

  last_combination_index = min(
    next_combination_index + config.ATTACK_BUNDLE_BATCH_SIZE, total_combinations
  )

  semaphore = asyncio.Semaphore(config.MAX_CONCURRENT_REQUESTS)
  calls = []

  for i in range(next_combination_index, last_combination_index):
    character_path, attack = combinations[i]
    character = load_character_with_rules(character_path)
    calls.append(
      generate_attacks_for_persona_and_attack(
        character_path, character, attack, semaphore
      )
    )

  results = await asyncio.gather(*calls, return_exceptions=True)

  successful = sum(1 for result in results if isinstance(result, int) and result == 0)
  print(f"Successfully generated {successful} attack prompt bundles.")

  errors = [result for result in results if (isinstance(result, int) and result != 0)]
  if errors:
    print(f"Encountered {len(errors)} errors during generation.")

  end = time.perf_counter()
  print(f"Attack prompt bundle generation completed in {end - start:.2f} seconds.")

  if last_combination_index >= total_combinations:
    print("Attack Prompt Bundle generation is complete. All combinations have been processed.")

  # Update the checkpoint
  checkpoint["next_combination_index"] = last_combination_index
  checkpoint["total_combinations"] = total_combinations
  checkpoint["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
  checkpoint_path.write_text(
    json.dumps(checkpoint, indent=2, ensure_ascii=False), encoding="utf-8"
  )

  return 0


asyncio.run(main())
