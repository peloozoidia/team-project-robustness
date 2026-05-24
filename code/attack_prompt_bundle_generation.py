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
  get_task_prompt,
)
from assets.attacks import attack_schema, get_test_collection
from misc.helpers import (
  extract_json_from_response,
  load_character_with_rules,
  output_path_for_attack,
)
from misc.llm_client import LLMClient

from misc.structured_pydantic_output import Attack,AttackBundle

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
          get_task_prompt(
            persona, attack
          ),
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

# =============================================================================
# NEW: Deterministic Template Support (Additional Functionality)
# =============================================================================
# The following functions provide deterministic template-based attack generation
# as an alternative to LLM-based generation. Original functionality above is unchanged.

async def generate_attacks_from_template(
  character_path, persona, attack, semaphore
) -> int:
  """
  NEW FUNCTION: Generate attacks using deterministic templates instead of LLM.
  
  This is an alternative to generate_attacks_for_persona_and_attack() that uses
  predefined templates for reproducible attack generation.
  """
  async with semaphore:
    try:
      from assets.attack_templates import generate_from_template
      
      try:
        Attack.model_validate(attack)
      except Exception as exc:
        print(f"Failed to validate attack object: {exc}", file=sys.stderr)
        return 1

      attack_key = attack.get("key", "")
      print(f"Using deterministic template for attack: {attack_key}")
      
      try:
        # Generate from template (no LLM call needed)
        template_bundles = generate_from_template(attack_key, persona)
        
        # Save each attack in the same format as LLM generation
        for prompts in template_bundles:
          data = {
            "attack_set_id": str(uuid.uuid4()),
            "attack": attack,
            "index": prompts["index"],
            "target_trait": prompts["target_trait"],
            "system_prompt": prompts["system_prompt"],
            "starting_prompt": prompts["starting_prompt"],
            "task_prompt": prompts["task_prompt"],
            "generation_method": "template",  # Mark as template-generated
          }
          out_path = output_path_for_attack(character_path, attack, data["index"])
          out_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
          )
      except Exception as exc:
        print(f"Template generation failed for {attack_key}: {exc}", file=sys.stderr)
        return 1

    except Exception as exc:
      print(
        f"Failed to generate prompts for {persona['name']}, attack {attack['key']}: {exc}",
        file=sys.stderr,
      )
      return 1

    return 0


async def generate_attacks_hybrid(
  character_path, persona, attack, semaphore
) -> int:
  """
  NEW FUNCTION: Hybrid approach - uses templates when available, falls back to LLM.
  
  This provides the best of both worlds: deterministic templates for consistency
  and LLM generation for attacks without templates.
  """
  async with semaphore:
    try:
      from assets.attack_templates import has_template, generate_from_template
      
      try:
        Attack.model_validate(attack)
      except Exception as exc:
        print(f"Failed to validate attack object: {exc}", file=sys.stderr)
        return 1

      attack_key = attack.get("key", "")
      
      # Check if a deterministic template exists for this attack type
      if has_template(attack_key):
        print(f"Using deterministic template for attack: {attack_key}")
        try:
          # Generate from template (no LLM call needed)
          template_bundles = generate_from_template(attack_key, persona)
          
          # Save each attack in the same format
          for prompts in template_bundles:
            data = {
              "attack_set_id": str(uuid.uuid4()),
              "attack": attack,
              "index": prompts["index"],
              "target_trait": prompts["target_trait"],
              "system_prompt": prompts["system_prompt"],
              "starting_prompt": prompts["starting_prompt"],
              "task_prompt": prompts["task_prompt"],
              "generation_method": "template",  # Mark as template-generated
            }
            out_path = output_path_for_attack(character_path, attack, data["index"])
            out_path.write_text(
              json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
            )
        except Exception as exc:
          print(f"Template generation failed for {attack_key}: {exc}", file=sys.stderr)
          return 1
      else:
        # Fall back to LLM-based generation (original behavior)
        print(f"Using LLM generation for attack: {attack_key}")
        llm = LLMClient(config.ATTACK_GENERATING_LLM)
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

        # Save each attack in a separate file
        for prompts in bundle.bundle:
          data = {
            "attack_set_id": str(uuid.uuid4()),
            "attack": attack,
            "index": prompts.index,
            "target_trait": prompts.target_trait,
            "system_prompt": prompts.system_prompt,
            "starting_prompt": prompts.starting_prompt,
            "task_prompt": prompts.task_prompt,
            "generation_method": "llm",  # Mark as LLM-generated
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


async def main_with_templates() -> int:
  """
  NEW FUNCTION: Alternative main() that uses hybrid generation (templates + LLM).
  
  To use this instead of the original main():
  1. Comment out: asyncio.run(main())
  2. Uncomment: asyncio.run(main_with_templates())
  """
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
      generate_attacks_hybrid(  # NEW: Use hybrid generation
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


# =============================================================================
# Main Execution
# =============================================================================
# Default: Use original LLM-based generation
asyncio.run(main())

# To enable hybrid mode (templates + LLM fallback), comment out the line above and uncomment:
# asyncio.run(main_with_templates())