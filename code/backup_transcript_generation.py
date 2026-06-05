import asyncio
import json
import time
from pathlib import Path

import config
from misc.helpers import (
  extract_json_from_file,
)
from misc.transcript_helpers import (
  get_missing_permutations,
  get_transcript_inputs,
  save_transcript,
)


async def main() -> int:
  start = time.perf_counter()

  transcript_permutations = get_transcript_inputs()
  missing_permutations = []

  semaphore = asyncio.Semaphore(config.MAX_CONCURRENT_REQUESTS)
  calls = []

  checkpoint_path = Path.cwd().joinpath("pipeline/checkpoint-transcripts.json")
  checkpoint = extract_json_from_file(checkpoint_path)

  missing_permutations = checkpoint["backup"]["missing_permutations"]
  if not missing_permutations:
    print(
      "No missing transcripts found in checkpoint. Checking for missing transcripts..."
    )
    missing_permutations = get_missing_permutations(transcript_permutations)
    checkpoint["backup"]["missing_permutations"] = missing_permutations
    print(f"Found {len(missing_permutations)} missing transcripts to generate.")

  total_transcripts = len(missing_permutations)
  next_transcript_index = int(checkpoint["backup"]["next_transcript_index"])
  if total_transcripts == 0:
    print("No missing transcripts found.")
    return 0

  last_transcript_index = min(
    next_transcript_index + config.TRANSCRIPT_BATCH_SIZE, total_transcripts
  )

  for i in range(next_transcript_index, last_transcript_index):
    (
      character_file,
      character_name,
      persona_prompt_strategy,
      persona_prompt,
      attack_prompt,
    ) = missing_permutations[i]
    calls.append(
      save_transcript(
        Path(character_file),
        character_name,
        persona_prompt_strategy,
        persona_prompt,
        attack_prompt,
        semaphore,
      )
    )

  results = await asyncio.gather(*calls, return_exceptions=True)

  successful = sum(1 for result in results if isinstance(result, int) and result == 0)
  print(f"Successfully generated {successful} missing attack transcripts.")

  errors = [result for result in results if (isinstance(result, int) and result != 0)]
  if errors:
    print(f"Encountered {len(errors)} errors during generation.")

  end = time.perf_counter()
  print(f"Transcript generation completed in {end - start:.2f} seconds.")

  if last_transcript_index >= total_transcripts:
    print(
      "Backup Transcript generation is complete. All backup transcripts have been generated."
    )
    checkpoint["backup"]["next_transcript_index"] = 0  # reset for potential reruns
    checkpoint["backup"]["total_transcripts"] = 0
  else:
    checkpoint["backup"]["next_transcript_index"] = last_transcript_index
    checkpoint["backup"]["total_transcripts"] = total_transcripts

  checkpoint["backup"]["updated_at"] = time.strftime(
    "%Y-%m-%d %H:%M:%S", time.localtime()
  )
  checkpoint_path.write_text(
    json.dumps(checkpoint, indent=2, ensure_ascii=False), encoding="utf-8"
  )

  return 0


asyncio.run(main())
