import json
import os
from pathlib import Path
import sys
import config
from misc.helpers import (
  load_character_with_rules,
  extract_prompt_bundle_from_response,
  output_path_for_attack,
  FinishedTaskGroup,
)
from misc.llm_client import LLMClient
import asyncio
from attacks import get_test_collection, attack_schema
import jsonschema
from prompts.attack_generating_llm import (
  SYSTEM_PROMPT,
  get_task_prompt,
  attack_bundle_schema,
)


async def generate_attacks_for_persona(character_path, persona, attacks) -> int:
  llm = LLMClient(config.ATTACK_GENERATING_LLM)
  for attack in attacks:
    try:
      jsonschema.validate(attack, attack_schema)
      response = llm.chat(SYSTEM_PROMPT, get_task_prompt(persona, attack, 2))
      response_json = extract_prompt_bundle_from_response(response)
      try:
        jsonschema.validate(
          response_json, attack_bundle_schema
        )  # validate to ensure LLM response is in the right schema
      except Exception as exc:
        print(f"Failed to validate LLM response: {exc}", file=sys.stderr)
        return 1

      # saving each attack in a separate file for easier dialogue generation
      for prompts in response_json["bundle"]:
        data = {
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
      return 1

  print(f"Saved all attack prompts for {persona['name']}")
  return 0


async def main() -> int:

  directory_path = Path(config.OUTPUT_PATH).joinpath("./characters")

  character_files = [
    directory_path.joinpath(character)
    for character in os.listdir(directory_path)
    if character.endswith(".json")
  ]

  attacks = get_test_collection(2)

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
