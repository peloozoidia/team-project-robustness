import math
import os
from pathlib import Path

import config
import pandas as pd
import numpy as np
from misc.helpers import extract_json_from_file, transform_transcript


def overlapping_chunks(
  df: pd.DataFrame,
  n_groups: int,
  groups_per_section: int,
) -> list[pd.DataFrame]:
  """Split df rows into overlapping chunks.

  Each chunk has length `n_groups * groups_per_section`.
  Chunks start every `ceil(len(df) / n_groups)` rows and wrap around if needed.
  """
  if n_groups < 1 or groups_per_section < 1:
    raise ValueError("n_groups and groups_per_section must be positive integers")

  total_rows = len(df)
  if total_rows == 0:
    return []

  section_size = math.ceil(total_rows / n_groups)
  chunk_size = section_size * groups_per_section

  chunks: list[pd.DataFrame] = []
  for i in range(n_groups):
    start = i * section_size
    indices = [(start + offset) % total_rows for offset in range(chunk_size)]
    chunks.append(df.iloc[indices].reset_index(drop=True))

  return chunks


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

  n_groups = 5
  groups_per_section = 2
  chunks = overlapping_chunks(csv, n_groups=n_groups, groups_per_section=groups_per_section)

  for i, chunk in enumerate(chunks, start=1):
    print(f"chunk_{i}: {len(chunk)} rows")
    chunk.to_excel(transcript_dir.joinpath(f"grouped_analysis_{i}.xlsx"), index=False)

  output_path = transcript_dir.joinpath("full_analysis.xlsx")
  csv.to_excel(output_path, index=False)