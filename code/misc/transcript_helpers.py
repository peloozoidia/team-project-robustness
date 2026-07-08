import json
import os
import sys
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


def get_transcript_inputs() -> list[tuple[Path, str, str, str, dict]]:
  character_dir = Path(config.OUTPUT_PATH).joinpath("./characters")
  persona_prompt_dir = Path(config.OUTPUT_PATH).joinpath("./persona_prompts")
  attack_prompt_dir = Path(config.OUTPUT_PATH).joinpath("./attack_prompts")

  character_files = [
    character_dir.joinpath(character)
    for character in os.listdir(character_dir)
    if character.endswith(".json")
  ]
  attack_prompt_files = [
    attack_prompt_dir.joinpath(file)
    for file in os.listdir(attack_prompt_dir)
    if file.endswith(".json")
  ]

  transcript_permutations = []

  for character_file in character_files:
    persona_prompt_file = [
      persona_prompt_dir.joinpath(file)
      for file in os.listdir(persona_prompt_dir)
      if file.startswith(character_file.stem)
    ][0]
    character_name, persona_prompt_bundle = extract_persona_prompt_bundle(
      persona_prompt_file
    )

    attack_prompts = [
      extract_json_from_file(file)
      for file in attack_prompt_files
      if file.stem.startswith(character_file.stem)
    ]

    if len(attack_prompts) == 0:
      continue

    if config.CHOSEN_PERSONA_STRATEGY:
      persona_prompt_strategy = list(persona_prompt_bundle.keys())[
        config.CHOSEN_PERSONA_STRATEGY - 1
      ]
      persona_prompt = persona_prompt_bundle[persona_prompt_strategy]

      for attack_prompt in attack_prompts:
        transcript_permutations.append(
          (
            character_file,
            character_name,
            persona_prompt_strategy,
            persona_prompt,
            attack_prompt,
          )
        )
    else:
      persona_prompt_count = 1
      for persona_prompt_strategy in persona_prompt_bundle:
        if persona_prompt_count > config.PERSONA_VARIATION_COUNT:
          break

        for attack_prompt in attack_prompts:
          transcript_permutations.append(
            (
              character_file,
              character_name,
              persona_prompt_strategy,
              persona_prompt_bundle[persona_prompt_strategy],
              attack_prompt,
            )
          )
        persona_prompt_count = persona_prompt_count + 1
  return transcript_permutations


def get_missing_permutations(
  all_combinations,
) -> list[tuple[str, str, str, str, dict]]:
  missing_permutations = []

  for (
    character_file,
    character_name,
    persona_prompt_strategy,
    persona_prompt,
    attack_prompt,
  ) in all_combinations:
    out_path = output_path_for_transcript(
      character_file,
      persona_prompt_strategy,
      attack_prompt["attack"],
      attack_prompt["index"],
    )

    if not out_path.is_file():
      missing_permutations.append(
        (
          str(character_file),
          character_name,
          persona_prompt_strategy,
          persona_prompt,
          attack_prompt,
        )
      )

  return missing_permutations


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
    return 0
  except Exception as exc:
    print(
      f"Failed to generate transcript for {character_file.stem}:{persona_prompt}, attack {attack['attack']['key']}:{attack['index']} :: {exc}",
      file=sys.stderr,
    )
    return 1


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
