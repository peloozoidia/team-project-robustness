import asyncio
import os
import time
from pathlib import Path

import config
from assets.attacks_per_character import (
  get_generated_attack_prompts,
  get_simple_command_attack_prompts,
  get_system_level_attack_prompts,
)
from misc.helpers import extract_persona_prompt_bundle, save_transcript
from misc.transcript_generators import (
  generate_basic_transcript,
  generate_simple_command_attack_transcript,
  generate_system_level_attack_transcript,
)


async def main():
  start = time.perf_counter()
  print("Starting extended transcript generation...")

  character_dir = Path(config.OUTPUT_PATH).joinpath("./characters")
  persona_prompt_dir = Path(config.OUTPUT_PATH).joinpath("./persona_prompts")

  character_files = [
    character_dir.joinpath(character)
    for character in os.listdir(character_dir)
    if character.endswith(".json")
  ]

  attack_setups = [
    (get_generated_attack_prompts, generate_basic_transcript),
    (get_system_level_attack_prompts, generate_system_level_attack_transcript),
    (get_simple_command_attack_prompts, generate_simple_command_attack_transcript),
  ]

  semaphore = asyncio.Semaphore(config.MAX_CONCURRENT_REQUESTS)
  calls = []

  for character_file in character_files:
    persona_prompt_file = [
      persona_prompt_dir.joinpath(file)
      for file in os.listdir(persona_prompt_dir)
      if file.startswith(character_file.stem)
    ][0]
    character_name, persona_prompt_bundle = extract_persona_prompt_bundle(
      persona_prompt_file
    )

    for attack_prompt_generator, attack_runner in attack_setups:
      attack_prompts = attack_prompt_generator(character_file)

      if config.CHOSEN_PERSONA_STRATEGY:
        persona_prompt_strategy = list(persona_prompt_bundle.keys())[
          config.CHOSEN_PERSONA_STRATEGY - 1
        ]
        persona_prompt = persona_prompt_bundle[persona_prompt_strategy]
        generations = [
          save_transcript(
            character_file,
            character_name,
            persona_prompt_strategy,
            persona_prompt,
            attack_prompt,
            attack_runner,
            semaphore,
          )
          for attack_prompt in attack_prompts
        ]
        calls.extend(generations)
      else:
        persona_prompt_count = 1
        for persona_prompt_strategy in persona_prompt_bundle:
          print(persona_prompt_strategy)
          if persona_prompt_count > config.PERSONA_VARIATION_COUNT:
            break

          generations = [
            save_transcript(
              character_file,
              character_name,
              persona_prompt_strategy,
              persona_prompt_bundle[persona_prompt_strategy],
              attack_prompt,
              attack_runner,
              semaphore,
            )
            for attack_prompt in attack_prompts
          ]
          calls.extend(generations)
          persona_prompt_count = persona_prompt_count + 1

  results = await asyncio.gather(*calls, return_exceptions=True)
  successful = sum(1 for result in results if isinstance(result, int) and result == 0)
  print(f"Successfully generated {successful} attack transcripts.")
  errors = [result for result in results if (isinstance(result, int) and result != 0)]
  if errors:
    print(f"Encountered {len(errors)} errors during generation.")

  end = time.perf_counter()
  print(f"Transcript generation completed in {end - start:.2f} seconds.")
  return 0


asyncio.run(main())
