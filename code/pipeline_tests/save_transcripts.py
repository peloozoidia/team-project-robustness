import os
from pathlib import Path

import config
import pandas as pd
from misc.helpers import extract_json_from_file, transform_transcript


def main() -> None:
  transcript_dir = Path(config.OUTPUT_PATH).joinpath("./transcripts")

  transcripts = [
    extract_json_from_file(transcript_dir.joinpath(file))
    for file in os.listdir(transcript_dir)
    if file.endswith(".json")
  ]

  df = pd.DataFrame.from_records(transcripts)

  csv = pd.DataFrame(df[["transcript_id", "character_name"]])

  csv["attack_name"] = df.apply(lambda row: row["attack_prompts"]["attack"]["name"], axis=1)
  csv["target_trait"] = df.apply(lambda row: row["attack_prompts"]["target_trait"], axis=1)

  csv["transcript_text"] = df.apply(
    lambda row: transform_transcript(row["transcript"]), axis=1
  )

  for index in range(0, config.TESTS_COUNT):
    csv[f"test_prompt_{index + 1}"] = df.apply(
      lambda row: row["attack_prompts"]["test_prompts"][index]["test"], axis=1
    )

  output_path = transcript_dir.joinpath("analysis.xlsx")
  csv.to_excel(output_path, index=False)
