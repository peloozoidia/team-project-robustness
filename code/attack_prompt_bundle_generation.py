import asyncio
import json
import os
import sys
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
  FinishedTaskGroup,
  extract_json_from_response,
  load_character_with_rules,
  output_path_for_attack,
)
from misc.llm_client import LLMClient


async def generate_attacks_for_persona(character_path, persona, attacks) -> int:
  errors = 0
  for attack in attacks:
    llm = LLMClient(config.ATTACK_GENERATING_LLM)
    try:
      jsonschema.validate(attack, attack_schema)
      response = llm.chat(SYSTEM_PROMPT, get_task_prompt(persona, attack, config.ATTACK_VARIATION_COUNT, config.TESTS_COUNT))
      response_json = extract_json_from_response(response)
      try:
        jsonschema.validate(
          response_json, get_attack_bundle_schema(config.ATTACK_VARIATION_COUNT, config.TESTS_COUNT)
        )  # validate to ensure LLM response is in the right schema
      except Exception as exc:
        print(f"Failed to validate LLM response: {exc}", file=sys.stderr)
        errors = errors + 1
        break

      # saving each attack in a separate file for easier dialogue generation
      for prompts in response_json["bundle"]:
        data = {
          "attack_set_id": str(uuid.uuid4()),
          "attack": attack,
          "index": prompts["index"],
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
      errors = errors + 1

  print(f"Saved attack prompts for {persona['name']}")
  return errors


async def main() -> int:

  directory_path = Path(config.OUTPUT_PATH).joinpath("./characters")

  character_files = [
    directory_path.joinpath(character)
    for character in os.listdir(directory_path)
    if character.endswith(".json")
  ][:1]

  attacks = get_test_collection(config.GENERATED_ATTACKS_COUNT)

  # using asynchronous functions for simultaneous execution
  async with FinishedTaskGroup() as tg:
    # read all character files and generate attack prompt bundles for each
    for character_path in character_files:
      character = load_character_with_rules(character_path)
      tg.create_task(
        generate_attacks_for_persona(character_path, character, attacks),
        name=character["name"],
      )

  errors = sum(tg.get_results())

  if errors != 0:
    print(f"Attack Prompt Generation failed: {errors} times")
    return 1

  print("Saved all attack prompts")
  return 0


asyncio.run(main())
