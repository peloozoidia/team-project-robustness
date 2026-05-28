import json
from pathlib import Path


def main():
  # Reset checkpoint files
  
  attack_bundle_checkpoint_path = Path.cwd().joinpath("pipeline/checkpoint-attack-bundles.json")
  attack_bundle_checkpoint_data = {
    "next_combination_index": 0,
    "total_combinations": 0,
    "updated_at": "",
  }
  attack_bundle_checkpoint_path.write_text(
    json.dumps(attack_bundle_checkpoint_data, indent=2, ensure_ascii=False),
    encoding="utf-8",
  )

  transcript_checkpoint_path = Path.cwd().joinpath("pipeline/checkpoint-transcripts.json")
  transcript_checkpoint_data = {
    "next_transcript_index": 0,
    "total_transcripts": 0,
    "updated_at": "",
  }
  transcript_checkpoint_path.write_text(
    json.dumps(transcript_checkpoint_data, indent=2, ensure_ascii=False),
    encoding="utf-8",
  )


main()
