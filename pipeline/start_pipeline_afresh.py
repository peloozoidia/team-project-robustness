import json
from pathlib import Path


def clear_output_folders():
   # Reset output folders
  output_path = Path.cwd().joinpath("outputs")
  characters_path = output_path.joinpath("characters")
  persona_prompts_path = output_path.joinpath("persona_prompts")
  attack_prompts_path = output_path.joinpath("attack_prompts")
  transcripts_path = output_path.joinpath("transcripts")
  results_path = output_path.joinpath("results")
  for path in [output_path, characters_path, persona_prompts_path, attack_prompts_path, transcripts_path, results_path]:
    if path.exists():
      if path not in []: #if path is not in the list of folders to keep, delete its contents
        for file in path.iterdir():
          if file.is_file():
            file.unlink()
    else:
      path.mkdir(parents=True, exist_ok=True)

def reset_checkpoints():
  # Reset checkpoint files
  attack_bundle_checkpoint_path = Path.cwd().joinpath("pipeline/checkpoint-attack-bundles.json")
  attack_bundle_checkpoint_data = {
    "next_combination_index": 0,
    "total_combinations": 0,
    "updated_at": "",
    "attacks": [],
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
    "backup": {
      "next_transcript_index": 0,
      "total_transcripts": 0,
      "updated_at": "",
      "missing_permutations": [],
    }
  }
  transcript_checkpoint_path.write_text(
    json.dumps(transcript_checkpoint_data, indent=2, ensure_ascii=False),
    encoding="utf-8",
  )

  evaluation_checkpoint_path = Path.cwd().joinpath("pipeline/checkpoint-evaluation.json")
  evaluation_checkpoint_data = {
    "next_evaluation_index": 0,
    "total_evaluations": 0,
    "updated_at": "",
    "evaluation_files": [],
    "all_evaluation_inputs": []
  }
  evaluation_checkpoint_path.write_text(
    json.dumps(evaluation_checkpoint_data, indent=2, ensure_ascii=False),
    encoding="utf-8",
  )

def main():
  print("Preparing pipeline to run afresh...")
  clear_output_folders()
  reset_checkpoints()
  print("Pipeline has been reset. You can now run the pipeline from the beginning.")

main()
