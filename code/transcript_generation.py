import json
import os
import sys
import uuid
from pathlib import Path

import config
from misc.helpers import (
  extract_json_from_file,
  extract_persona_prompt_bundle,
  output_path_for_transcript,
)
from misc.llm_client import LLMClient


def main() -> int:
  character_dir = Path(config.OUTPUT_PATH).joinpath("./characters")
  persona_prompt_dir = Path(config.OUTPUT_PATH).joinpath("./persona_prompts")
  attack_prompt_dir = Path(config.OUTPUT_PATH).joinpath("./attack_prompts")

  character_files = [
    character_dir.joinpath(character)
    for character in os.listdir(character_dir)
    if character.endswith(".json")
  ]

  errors = 0

  for character_file in character_files:
    persona_prompt_file = [
      persona_prompt_dir.joinpath(file)
      for file in os.listdir(persona_prompt_dir)
      if file.startswith(character_file.stem)
    ][0]
    persona_prompt_bundle = extract_persona_prompt_bundle(persona_prompt_file)

    attack_prompt_files = [
      attack_prompt_dir.joinpath(file)
      for file in os.listdir(attack_prompt_dir)
      if file.startswith(character_file.stem)
    ]

    if attack_prompt_files.__len__() == 0:
      break

    attack_prompts = [extract_json_from_file(file) for file in attack_prompt_files]

    persona_prompt_count = 1
    for persona_prompt in persona_prompt_bundle:
      print(persona_prompt)
      if persona_prompt_count == 1:  # TEMPORARY!
        persona_prompt_count = persona_prompt_count + 1
        continue
      if persona_prompt_count > config.PERSONA_VARIATION_COUNT:
        break

      for attack_prompt in attack_prompts:  # this is a list
        try:
          transcript = generate_transcript(
            persona_prompt_bundle[persona_prompt], attack_prompt, config.NUM_TURNS
          )

          data = {
            "transcript_id": str(uuid.uuid4()),
            "persona_llm": config.MODELS[config.PERSONA_LLM],
            "attacker_llm": config.MODELS[config.ATTACKING_LLM],
            "persona_prompt_strategy": persona_prompt,
            "attack_prompts": attack_prompt,
            "transcript": transcript,
          }

          out_path = output_path_for_transcript(
            character_file,
            persona_prompt,
            attack_prompt["attack"],
            attack_prompt["index"],
          )
          out_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
          )
          print("** Saved Transcript **")
        except Exception as exc:
          print(
            f"Failed to generate transcript for {character_file.stem}:{persona_prompt}, attack {attack_prompt['attack']['key']}:{attack_prompt['index']} :: {exc}",
            file=sys.stderr,
          )
          errors = errors + 1

      persona_prompt_count = persona_prompt_count + 1

    print(f"Finished generating transcripts for {character_file.stem}")

  print("Finished generating all transcripts")
  return 0


def generate_transcript(persona, attack, N=3) -> list[dict]:
  attacker_llm = LLMClient(config.ATTACKING_LLM)
  persona_llm = LLMClient(config.PERSONA_LLM)

  shared_history: list[dict[str, str]] = []
  transcript: list[dict] = []

  for turn_index in range(1, N + 1):  # N-shot attack
    if turn_index == 1:
      attack_prompt = attack["starting_prompt"]
    else:
      attack_prompt = attack["task_prompt"]

    print(f"Prompting Addy... Turn {turn_index}")
    attacker_text = attacker_llm.chat(
      attack["system_prompt"], attack_prompt, shared_history, 0.65
    )
    transcript.append({"turn": turn_index, "speaker": "user", "text": attacker_text})

    print(f"Prompting NPC... Turn {turn_index}")
    persona_text = persona_llm.chat(persona, attacker_text, shared_history, 0.65)
    transcript.append({"turn": turn_index, "speaker": "npc", "text": persona_text})

    shared_history.append({"role": "user", "content": attacker_text})
    shared_history.append({"role": "assistant", "content": persona_text})

  return transcript


main()
