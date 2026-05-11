import os
from pathlib import Path

import config
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from misc.helpers import extract_json_from_file


def main() -> None:
  output_dir = Path(config.OUTPUT_PATH).joinpath("./results")

  eval_files = [
    output_dir.joinpath(eval_file)
    for eval_file in os.listdir(output_dir)
    if eval_file.endswith(".json") and eval_file.startswith("eval_result")
  ]

  df_full = pd.DataFrame()

  human_eval_files = [
    output_dir.joinpath(eval_file)
    for eval_file in os.listdir(output_dir)
    if eval_file.endswith(".json") and eval_file.startswith("human_eval_result")
  ]

  df_human = pd.DataFrame()

  for f in eval_files:
    json_raw = extract_json_from_file(output_dir.joinpath(f))
    df = pd.DataFrame(json_raw["results"])
    df_full = pd.DataFrame(pd.concat([df_full, df]))

  for f in human_eval_files:
    json_raw = extract_json_from_file(output_dir.joinpath(f))
    df = pd.DataFrame(json_raw["results"])
    df_human = pd.DataFrame(pd.concat([df_human, df]))

  df = df_full.groupby(["transcript_id"]).mean(numeric_only=True)
  df = df.rename(
    columns={
      "test_score": "mean_score",
      "always_test_score": "mean_always_score",
      "never_test_score": "mean_never_score",
    }
  )

  df_human = df_human.groupby(["transcript_id"]).mean(numeric_only=True)
  df_human = df_human.rename(
    columns={
      "test_score": "mean_human_score",
      "always_test_score": "mean_human_always_score",
      "never_test_score": "mean_human_never_score",
    }
  )

  unique_transcripts = pd.DataFrame(extract_json_from_file(eval_files[0])["results"])
  results = unique_transcripts.drop(columns=["test_score", "test_results"])
  results = results.join(df, on="transcript_id")
  results = results.join(df_human, on="transcript_id")

  print(
    f"Correlation of total scores: {results.mean_score.corr(results.mean_human_score)}"
  )
  print(
    f"Correlation of always test scores: {results.mean_always_score.corr(results.mean_human_always_score)}"
  )
  print(
    f"Correlation of never test scores: {results.mean_never_score.corr(results.mean_human_never_score)}"
  )

  fig = plt.figure()
  plt.hist(
    results.mean_score,
    bins=[0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0],
    label="LLM Evaluation",
    alpha=0.5,
  )
  plt.hist(
    results.mean_human_score,
    bins=[0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0],
    label="Human Evaluation",
    alpha=0.5,
  )
  plt.ylabel("Frequency")
  plt.xlabel("Passed Tests per Attack")
  plt.title("Overall Test Score Frequency")
  plt.legend()
  fig.savefig(
    fname=output_dir.joinpath("test_scores_overall.svg"),
    format="svg",
    bbox_inches="tight",
  )
  fig.clear()

  fig = plt.figure()
  plt.hist(
    results.mean_always_score,
    bins=[0.0, 0.5, 1.0, 1.5, 2.0],
    label="LLM Evaluation",
    alpha=0.5,
  )
  plt.hist(
    results.mean_human_always_score,
    bins=[0.0, 0.5, 1.0, 1.5, 2.0],
    label="Human Evaluation",
    alpha=0.5,
  )
  plt.ylabel("Frequency")
  plt.xlabel("Passed Tests per Attack")
  plt.title("Always Test Score Frequency")
  plt.legend()
  fig.savefig(
    fname=output_dir.joinpath("test_scores_always.svg"),
    format="svg",
    bbox_inches="tight",
  )
  fig.clear()

  fig = plt.figure()
  plt.hist(
    results.mean_never_score,
    bins=[0.0, 0.5, 1.0, 1.5, 2.0],
    label="LLM Evaluation",
    alpha=0.5,
  )
  plt.hist(
    results.mean_human_never_score,
    bins=[0.0, 0.5, 1.0, 1.5, 2.0],
    label="Human Evaluation",
    alpha=0.5,
  )
  plt.ylabel("Frequency")
  plt.xlabel("Passed Tests per Attack")
  plt.title("Never Test Score Frequency")
  plt.legend()
  fig.savefig(
    fname=output_dir.joinpath("test_scores_never.svg"),
    format="svg",
    bbox_inches="tight",
  )
  fig.clear()

  results_by_char = results.groupby(["character"]).sum(numeric_only=True)
  x = np.arange(len(results_by_char))
  width = 1 / 3
  fig, ax = plt.subplots()
  bars = ax.bar(x, results_by_char.mean_score, width=width, label="LLM Evaluation")
  ax.bar_label(
    bars, labels=[round(score, 2) for score in results_by_char.mean_score], padding=2
  )
  bars = ax.bar(
    x + width, results_by_char.mean_human_score, width=width, label="Human Evaluation"
  )
  ax.bar_label(
    bars, labels=[round(score) for score in results_by_char.mean_human_score], padding=2
  )
  ax.legend()
  ax.set_ylabel("Total score")
  ax.set_xlabel("Total passed tests per Character")
  ax.set_title("Character-Wise Breakdown")
  ax.set_xticks(x + width / 2, results_by_char.index)
  plt.draw()
  for tick in ax.get_xticklabels():
    tick.set_rotation(90)
  fig.savefig(
    fname=output_dir.joinpath("test_scores_by_char.svg"),
    format="svg",
    bbox_inches="tight",
  )
  fig.clear()

  results_by_persona_key = results.groupby(["persona_key"]).sum(numeric_only=True)
  x = np.arange(len(results_by_persona_key))
  width = 1 / 3
  fig, ax = plt.subplots()
  bars = ax.bar(
    x, results_by_persona_key.mean_score, width=width, label="LLM Evaluation"
  )
  ax.bar_label(
    bars,
    labels=[round(score, 2) for score in results_by_persona_key.mean_score],
    padding=2,
  )
  bars = ax.bar(
    x + width,
    results_by_persona_key.mean_human_score,
    width=width,
    label="Human Evaluation",
  )
  ax.bar_label(
    bars,
    labels=[round(score) for score in results_by_persona_key.mean_human_score],
    padding=2,
  )
  ax.legend()
  ax.set_ylabel("Total score")
  ax.set_xlabel("Total passed tests per Prompt Strategy")
  ax.set_title("Prompt Strategy-Wise")
  ax.set_xticks(x + width / 2, results_by_persona_key.index)
  plt.draw()
  for tick in ax.get_xticklabels():
    tick.set_rotation(90)
  fig.savefig(
    fname=output_dir.joinpath("test_scores_by_prompt_strat.svg"),
    format="svg",
    bbox_inches="tight",
  )
  fig.clear()

  results_by_attack_key = results.groupby(["attack_key"]).sum(numeric_only=True)
  x = np.arange(len(results_by_attack_key))
  width = 1 / 3
  fig, ax = plt.subplots()
  bars = ax.bar(
    x, results_by_attack_key.mean_score, width=width, label="LLM Evaluation"
  )
  ax.bar_label(
    bars,
    labels=[round(score, 2) for score in results_by_attack_key.mean_score],
    padding=2,
  )
  bars = ax.bar(
    x + width,
    results_by_attack_key.mean_human_score,
    width=width,
    label="Human Evaluation",
  )
  ax.bar_label(
    bars,
    labels=[round(score) for score in results_by_attack_key.mean_human_score],
    padding=2,
  )
  ax.set_ylabel("Total score")
  ax.set_xlabel("Total passed tests per Attack")
  ax.set_title("Attack-Wise Breakdown")
  ax.set_xticks(x + width / 2, results_by_attack_key.index)
  ax.legend()
  plt.draw()
  for tick in ax.get_xticklabels():
    tick.set_rotation(90)
  fig.savefig(
    fname=output_dir.joinpath("test_scores_by_attack.svg"),
    format="svg",
    bbox_inches="tight",
  )
  fig.clear()


main()
