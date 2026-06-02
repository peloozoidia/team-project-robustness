import json
import os
import sys
from pathlib import Path

import config
from misc import generate_prompts


def main() -> int:

  directory_path = Path(config.OUTPUT_PATH).joinpath("./characters")

  character_files = [
    directory_path.joinpath(character)
    for character in os.listdir(directory_path)
    if character.endswith(".json")
  ]

  # read all character files and generate prompt bundles for each
  for character_path in character_files:
    try:
      character = generate_prompts.load_character(character_path)
      # llm = llm_client.LLMClient(config.PERSONA_GENERATING_LLM)
      bundle = generate_prompts.build_prompt_bundle(character, llm=None)
      out_path = generate_prompts.output_path_for(character_path)
      out_path.write_text(
        json.dumps(bundle, indent=2, ensure_ascii=False), encoding="utf-8"
      )
    except Exception as exc:
      print(f"Failed to generate prompts: {exc}", file=sys.stderr)
      return 1
    print(f"Saved prompts to: {out_path}")

  print("Saved all prompts")

  return 0


main()
