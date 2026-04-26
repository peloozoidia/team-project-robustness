import os
from pathlib import Path

import config
import matplotlib.pyplot as plt
import pandas as pd
from misc.helpers import extract_json_from_file


def main() -> None:
  output_dir = Path(config.OUTPUT_PATH).joinpath("./results")

  eval_files = [
    output_dir.joinpath(eval_file)
    for eval_file in os.listdir(output_dir)
    if eval_file.endswith(".json")
  ]

  df_full = pd.DataFrame()

  for f in eval_files:
    json_raw = extract_json_from_file(output_dir.joinpath(f))
    df = pd.DataFrame(json_raw["results"])
    df_full = pd.DataFrame(pd.concat([df_full, df]))

  df = df_full.groupby(["transcript_id"]).mean(numeric_only=True)
  df = df.rename(columns={"test_score": "mean_score"})

  unique_transcripts = pd.DataFrame(extract_json_from_file(eval_files[0])["results"])
  results = unique_transcripts.drop(columns=["test_score", "test_results"])
  results = results.join(df, on="transcript_id")

  fig = plt.figure()
  plt.hist(results.mean_score, bins=[1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0])
  plt.ylabel("Frequency")
  plt.xlabel("Passed Tests per Attack")
  plt.title("Overall Test Score Frequency")
  fig.savefig(fname=output_dir.joinpath("test_scores_overall.svg"), format="svg", bbox_inches="tight")
  fig.clear()

  results_by_char = results.groupby(["character"]).sum(numeric_only=True)
  fig, ax = plt.subplots()
  bars = plt.bar(results_by_char.index, results_by_char.mean_score)
  plt.bar_label(bars, labels=results_by_char.mean_score, padding=1)
  plt.ylabel("Total score")
  plt.xlabel("Total passed tests per Character")
  plt.title("Character-Wise Breakdown")
  plt.draw()
  for tick in ax.get_xticklabels():
    tick.set_rotation(90)
  fig.savefig(fname=output_dir.joinpath("test_scores_by_char.svg"), format="svg", bbox_inches="tight")
  fig.clear()

  results_by_persona_key = results.groupby(["persona_key"]).sum(numeric_only=True)
  fig, ax = plt.subplots()
  bars = plt.bar(results_by_persona_key.index, results_by_persona_key.mean_score)
  plt.bar_label(bars, labels=results_by_persona_key.mean_score, padding=1)
  plt.ylabel("Total score")
  plt.xlabel("Total passed tests per Prompt Strategy")
  plt.title("Prompt Strategy-Wise")
  plt.draw()
  for tick in ax.get_xticklabels():
    tick.set_rotation(90)
  fig.savefig(
    fname=output_dir.joinpath("test_scores_by_prompt_strat.svg"), format="svg", bbox_inches="tight"
  )
  fig.clear()

  results_by_attack_key = results.groupby(["attack_key"]).sum(numeric_only=True)
  fig, ax = plt.subplots()
  bars = plt.bar(results_by_attack_key.index, results_by_attack_key.mean_score)
  plt.bar_label(bars, labels=results_by_attack_key.mean_score, padding=1)
  plt.ylabel("Total score")
  plt.xlabel("Total passed tests per Attack")
  plt.title("Attack-Wise Breakdown")
  plt.draw()
  for tick in ax.get_xticklabels():
    tick.set_rotation(90)
  fig.savefig(fname=output_dir.joinpath("test_scores_by_attack.svg"), format="svg", bbox_inches="tight")
  fig.clear()


main()
