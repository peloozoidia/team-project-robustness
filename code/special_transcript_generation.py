import asyncio
import os
import time
from pathlib import Path

import config
from assets.special_attack_template import system_level_attack_prompts
from misc.helpers import extract_persona_prompt_bundle, is_refusal, save_transcript
from misc.llm_client import LLMClient


async def run_system_level_attack(persona, attack, semaphore, N=3) -> list[dict]:
  async with semaphore:
    attacker_llm = LLMClient(config.ATTACKING_LLM)
    persona_llm = LLMClient(config.PERSONA_LLM)

    shared_history: list[dict[str, str]] = []
    transcript: list[dict] = []

    for turn_index in range(1, N + 1):  # N-shot attack
      if turn_index == 1:
        attack_prompt = attack["starting_prompt_verbatim"]
        attacker_text = attack_prompt
      else:
        attack_prompt = attack["task_prompt"]
        attacker_text = await attacker_llm.asyncChat(
          attack["system_prompt"], attack_prompt, shared_history, 0.4
        )

      if is_refusal(attacker_text):
        print(f"Attacker refused to continue at turn {turn_index}. Ending transcript.")
        break
      transcript.append({"turn": turn_index, "speaker": "user", "text": attacker_text})

      persona_text = await persona_llm.asyncChat(
        persona, attacker_text, shared_history, 0.4
      )
      transcript.append({"turn": turn_index, "speaker": "npc", "text": persona_text})

      shared_history.append({"role": "user", "content": attacker_text})
      shared_history.append({"role": "assistant", "content": persona_text})

    return transcript

async def main():
  start = time.perf_counter()
  print("Starting SPECIAL transcript generation...")

  character_dir = Path(config.OUTPUT_PATH).joinpath("./characters")
  persona_prompt_dir = Path(config.OUTPUT_PATH).joinpath("./persona_prompts")

  character_files = [
    character_dir.joinpath(character)
    for character in os.listdir(character_dir)
    if character.endswith(".json")
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

    attack_prompts = system_level_attack_prompts(character_file)
    
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
          run_system_level_attack,
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
            run_system_level_attack,
            semaphore,
          )
          for attack_prompt in attack_prompts
        ]
        calls.extend(generations)
        persona_prompt_count = persona_prompt_count + 1
    
  results = await asyncio.gather(*calls, return_exceptions=True)
  successful = sum(1 for result in results if isinstance(result, int) and result == 0)
  print(f"Successfully generated {successful} special attack transcripts.")
  errors = [result for result in results if (isinstance(result, int) and result != 0)]
  if errors:
    print(f"Encountered {len(errors)} errors during generation.")

  end = time.perf_counter()
  print(f"Special transcript generation completed in {end - start:.2f} seconds.")
  return 0

asyncio.run(main())