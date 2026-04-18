import json
from pathlib import Path
import os

import config
import matplotlib.pyplot as plt
import pandas as pd


def main() -> None:
  output_dir = Path(config.OUTPUT_PATH).joinpath("./results")

  eval_files = [
    output_dir.joinpath(eval_file)
    for eval_file in os.listdir(output_dir)
    if eval_file.endswith(".json")
  ]

  df_full = pd.DataFrame()

  for f in eval_files:
    json_raw = json.loads(output_dir.joinpath(f).read_text(encoding="utf-8").replace("‑", "-"))
    df = pd.DataFrame(json_raw["results"])
    df["variant"] = f.stem
    df_full = pd.DataFrame(pd.concat([df_full, df]))

  df = df_full.groupby(["character", "persona_key", "attack_key"]).mean(numeric_only=True)
  print(df)

  fig = plt.figure()
  # score_counts = [(df.test_score == score).sum() for score in scores]
  plt.hist(df.test_score, bins=[1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0])
  plt.ylabel("Frequency")
  plt.xlabel("Passed Tests per Attack")
  plt.title("Overall Test Score Frequency")
  fig.savefig(fname=output_dir.joinpath("test_scores_overall.png"), format="png")
  fig.clear()

  df_by_char = df.groupby(["character"]).sum(numeric_only=True)
  fig = plt.figure()
  plt.bar(df_by_char.index, df_by_char["test_score"])
  plt.ylabel("Total score")
  plt.xlabel("Total passed tests per Character")
  fig.savefig(fname=output_dir.joinpath("test_scores_by_char.png"), format="png")
  fig.clear()

  df_by_persona_key = df.groupby(["persona_key"]).sum(numeric_only=True)
  fig = plt.figure(figsize=(20, 12))
  plt.barh(df_by_persona_key.index, df_by_persona_key["test_score"])
  plt.xlabel("Total score")
  plt.ylabel("Total passed tests per Prompt Strategy")
  fig.savefig(fname=output_dir.joinpath("test_scores_by_prompt_strat.png"), format="png")
  fig.clear()


main()