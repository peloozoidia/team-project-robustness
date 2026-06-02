import asyncio
import json
import time
from pathlib import Path

import config
from misc.helpers import (
  extract_json_from_file,
)
from misc.transcript_helpers import get_transcript_inputs, save_transcript


async def main() -> int:
  start = time.perf_counter()

  checkpoint_path = Path.cwd().joinpath("pipeline/checkpoint-transcripts.json")
  checkpoint = extract_json_from_file(checkpoint_path)

  transcript_inputs = get_transcript_inputs()

  total_transcripts = len(transcript_inputs)
  next_transcript_index = int(checkpoint["next_transcript_index"])
  if next_transcript_index >= total_transcripts:
    print("All transcripts have already been generated.")
    return 0

  last_transcript_index = min(
    next_transcript_index + config.TRANSCRIPT_BATCH_SIZE, total_transcripts
  )

  semaphore = asyncio.Semaphore(config.MAX_CONCURRENT_REQUESTS)
  calls = []  # saves only the calls run in this batch

  for i in range(next_transcript_index, last_transcript_index):
    (
      character_file,
      character_name,
      persona_prompt_strategy,
      persona_prompt,
      attack_prompt,
    ) = transcript_inputs[i]
    calls.append(
      save_transcript(
        character_file,
        character_name,
        persona_prompt_strategy,
        persona_prompt,
        attack_prompt,
        semaphore,
      )
    )

  results = await asyncio.gather(*calls, return_exceptions=True)

  successful = sum(1 for result in results if isinstance(result, int) and result == 0)
  print(f"Successfully generated {successful} attack transcripts.")

  errors = [result for result in results if (isinstance(result, int) and result != 0)]
  if errors:
    print(f"Encountered {len(errors)} errors during generation.")

  end = time.perf_counter()
  print(f"Transcript generation completed in {end - start:.2f} seconds.")

  if last_transcript_index >= total_transcripts:
    print("Transcript generation is complete. All transcripts have been generated.")

  # Update the checkpoint
  checkpoint["next_transcript_index"] = last_transcript_index
  checkpoint["total_transcripts"] = total_transcripts
  checkpoint["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
  checkpoint_path.write_text(
    json.dumps(checkpoint, indent=2, ensure_ascii=False), encoding="utf-8"
  )

  return 0


asyncio.run(main())
