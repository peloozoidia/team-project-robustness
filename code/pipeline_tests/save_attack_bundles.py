import os
from pathlib import Path

import config
import pandas as pd
from misc.helpers import extract_json_from_file


def main() -> None:
  attack_prompt_dir = Path(config.OUTPUT_PATH).joinpath("./attack_prompts")

  attack_prompts = [
    extract_json_from_file(attack_prompt_dir.joinpath(file))
    for file in os.listdir(attack_prompt_dir)
    if file.endswith('.json')
  ]

  df = pd.DataFrame.from_records(attack_prompts)

  csv = pd.DataFrame(df[["attack_set_id", "system_prompt", "starting_prompt", "task_prompt"]])
  csv["attack_name"] = df.apply(lambda row: row['attack']['name'], axis=1)
  csv["attack_description"] = df.apply(lambda row: row['attack']['description'], axis=1)

  for index in range(0, config.TESTS_COUNT):
    csv[f"test_prompt_{index+1}"] = df.apply(lambda row: row['test_prompts'][index]['test'], axis=1)

  output_path = attack_prompt_dir.joinpath('analysis.xlsx')
  csv.to_excel(output_path, columns=["attack_set_id", "attack_name", "attack_description", "system_prompt", "starting_prompt", "task_prompt", "test_prompt_1", "test_prompt_2", "test_prompt_3", "test_prompt_4", "test_prompt_5"], index=False)
