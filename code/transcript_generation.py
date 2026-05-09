import asyncio
import json
import os
import sys
import time
import uuid
from pathlib import Path

import config
from misc.helpers import (
  extract_json_from_file,
  extract_persona_prompt_bundle,
  is_refusal,
  output_path_for_transcript,
)
from misc.llm_client import LLMClient


async def main() -> int:
  start = time.perf_counter()

  character_dir = Path(config.OUTPUT_PATH).joinpath("./characters")
  persona_prompt_dir = Path(config.OUTPUT_PATH).joinpath("./persona_prompts")
  attack_prompt_dir = Path(config.OUTPUT_PATH).joinpath("./attack_prompts")

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

    attack_prompt_files = [
      attack_prompt_dir.joinpath(file)
      for file in os.listdir(attack_prompt_dir)
      if file.startswith(character_file.stem)
    ]

    if attack_prompt_files.__len__() == 0:
      break

    attack_prompts = [extract_json_from_file(file) for file in attack_prompt_files]

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
          semaphore,
        )
        for attack_prompt in attack_prompts
      ]
      calls.extend(generations)
    else:
      persona_prompt_count = 1
      for persona_prompt_strategy in persona_prompt_bundle:
        if persona_prompt_count > config.PERSONA_VARIATION_COUNT:
          break

        generations = [
          save_transcript(
            character_file,
            character_name,
            persona_prompt_strategy,
            persona_prompt_bundle[persona_prompt_strategy],
            attack_prompt,
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
  print(f"Attack prompt bundle generation completed in {end - start:.2f} seconds.")
  return 0


async def generate_transcript(persona, attack, semaphore, N=3) -> list[dict]:
  async with semaphore:
    attacker_llm = LLMClient(config.ATTACKING_LLM)
    persona_llm = LLMClient(config.PERSONA_LLM)

    shared_history: list[dict[str, str]] = []
    transcript: list[dict] = []

    for turn_index in range(1, N + 1):  # N-shot attack
      if turn_index == 1:
        attack_prompt = attack["starting_prompt"]
      else:
        attack_prompt = attack["task_prompt"]

      # print(f"Prompting Addy... Turn {turn_index}")
      attacker_text = await attacker_llm.asyncChat(
        attack["system_prompt"], attack_prompt, shared_history, 0.4
      )
      if is_refusal(attacker_text):
        print(f"Attacker refused to continue at turn {turn_index}. Ending transcript.")
        break
      transcript.append({"turn": turn_index, "speaker": "user", "text": attacker_text})

      # print(f"Prompting NPC... Turn {turn_index}")
      persona_text = await persona_llm.asyncChat(
        persona, attacker_text, shared_history, 0.4
      )
      transcript.append({"turn": turn_index, "speaker": "npc", "text": persona_text})

      shared_history.append({"role": "user", "content": attacker_text})
      shared_history.append({"role": "assistant", "content": persona_text})

    return transcript


async def save_transcript(
  character_file, character_name, persona_prompt, persona, attack, semaphore
) -> int:
  try:
    transcript = await generate_transcript(
      persona, attack, semaphore=semaphore, N=config.NUM_TURNS
    )

    if not transcript:
      print(
        f"No transcript generated for {character_file.stem}:{persona_prompt}, attack {attack['attack']['key']}:{attack['index']}",
        file=sys.stderr,
      )
      return 1

    data = {
      "transcript_id": str(uuid.uuid4()),
      "persona_llm": config.MODELS[config.PERSONA_LLM],
      "attacker_llm": config.MODELS[config.ATTACKING_LLM],
      "character_name": character_name,
      "persona_prompt_strategy": persona_prompt,
      "attack_prompts": attack,
      "transcript": transcript,
    }

    out_path = output_path_for_transcript(
      character_file,
      persona_prompt,
      attack["attack"],
      attack["index"],
    )
    out_path.write_text(
      json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print("** Saved Transcript **")
    return 0
  except Exception as exc:
    print(
      f"Failed to generate transcript for {character_file.stem}:{persona_prompt}, attack {attack['attack']['key']}:{attack['index']} :: {exc}",
      file=sys.stderr,
    )
    return 1


asyncio.run(main())
