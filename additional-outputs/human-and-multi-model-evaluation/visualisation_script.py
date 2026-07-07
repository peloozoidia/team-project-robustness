import os
import re
from pathlib import Path

import config
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
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

  df_full = df_full.replace(np.nan, "gpt-oss:20b-cloud")

  df = df_full.groupby(["transcript_id", "evaluating_model"]).mean(numeric_only=True)
  df = df.rename(
    columns={
      "test_score": "mean_score",
      "always_test_score": "mean_always_score",
      "never_test_score": "mean_never_score",
    }
  )

  def sanitize_label(label: str) -> str:
    return "_".join([token for token in re.split(r"[^0-9A-Za-z]+", label) if token])

  model_labels: list[tuple[str, str]] = []
  model_dfs: dict[str, pd.DataFrame] = {}

  for evaluating_model in sorted(
    df.index.get_level_values("evaluating_model").unique()
  ):
    suffix = sanitize_label(evaluating_model)
    model_labels.append((evaluating_model, suffix))
    model_df = df.xs(evaluating_model, level="evaluating_model").copy()
    model_df = model_df.rename(
      columns={
        "mean_score": f"mean_score_{suffix}",
        "mean_always_score": f"mean_always_score_{suffix}",
        "mean_never_score": f"mean_never_score_{suffix}",
      }
    )  # type: ignore
    model_dfs[evaluating_model] = model_df

  df_human = df_human.groupby(["transcript_id"]).mean(numeric_only=True)
  df_human = df_human.rename(
    columns={
      "test_score": "mean_score",
      "always_test_score": "mean_always_score",
      "never_test_score": "mean_never_score",
    }
  )

  unique_transcripts = pd.DataFrame(extract_json_from_file(eval_files[0])["results"])
  unique_transcripts = unique_transcripts.replace(np.nan, "gpt-oss:20b-cloud")
  results = unique_transcripts.drop(
    columns=["test_score", "test_results"], errors="ignore"
  )
  results = results.drop_duplicates(subset=["transcript_id"]).set_index("transcript_id")

  results = results.join(df_human, how="left")
  for evaluating_model, suffix in model_labels:
    results = results.join(model_dfs[evaluating_model], how="left")

  stats = [
    ("mean_score", "total"),
    ("mean_always_score", "always"),
    ("mean_never_score", "never"),
  ]

  correlation_data = []

  for evaluating_model, suffix in model_labels:
    for metric, label in stats:
      model_col = f"{metric}_{suffix}"
      if model_col in results.columns:
        corr_value = results[metric].corr(results[model_col])
        correlation_data.append(
          {
            "Comparison Type": "Human vs. Model",
            "Model 1": "Human Evaluation",
            "Model 2": evaluating_model,
            "Metric": label,
            "Correlation": corr_value,
          }
        )
      else:
        print(f"  Missing column for {model_col}, skipping.")

  if len(model_labels) > 1:
    for i in range(len(model_labels)):
      for j in range(i + 1, len(model_labels)):
        model_a, suffix_a = model_labels[i]
        model_b, suffix_b = model_labels[j]
        for metric, label in stats:
          col_a = f"{metric}_{suffix_a}"
          col_b = f"{metric}_{suffix_b}"
          if col_a in results.columns and col_b in results.columns:
            corr_value = results[col_a].corr(results[col_b])
            correlation_data.append(
              {
                "Comparison Type": "Model vs. Model",
                "Model 1": model_a,
                "Model 2": model_b,
                "Metric": label,
                "Correlation": corr_value,
              }
            )
          else:
            print(f"  Missing columns for {col_a} or {col_b}, skipping.")

  df_correlations = pd.DataFrame(correlation_data)
  if not df_correlations.empty:
    corr_file = output_dir.joinpath("correlations.xlsx")
    df_correlations.to_excel(corr_file, index=False, engine="openpyxl")
    print(f"\nCorrelations saved to {corr_file}")

  def plot_histogram(metric: str, title: str, bins: list[float], filename: str) -> None:
    fig, ax = plt.subplots(figsize=(9, 6))
    human_values = results[metric].dropna()
    ax.hist(human_values, bins=bins, alpha=0.35, label="Human Evaluation")

    for evaluating_model, suffix in model_labels:
      column = f"{metric}_{suffix}"
      if column not in results.columns:
        continue
      model_values = results[column].dropna()
      ax.hist(
        model_values,
        bins=bins,
        alpha=0.35,
        label=f"{evaluating_model}",
      )

    ax.set_ylabel("Frequency")
    ax.set_xlabel("Passed Tests per Attack")
    ax.set_title(title)
    ax.legend()
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(output_dir.joinpath(filename), format="svg", bbox_inches="tight")
    plt.close(fig)

  plot_histogram(
    "mean_score",
    "Overall Test Score Frequency",
    [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0],
    "test_scores_overall.svg",
  )
  plot_histogram(
    "mean_always_score",
    "Always Test Score Frequency",
    [0.0, 0.5, 1.0, 1.5, 2.0],
    "test_scores_always.svg",
  )
  plot_histogram(
    "mean_never_score",
    "Never Test Score Frequency",
    [0.0, 0.5, 1.0, 1.5, 2.0],
    "test_scores_never.svg",
  )

  def plot_grouped_bars(group_key: str, title: str, filename: str) -> None:
    grouped = results.groupby(group_key).sum(numeric_only=True)
    display_columns = [("Human Evaluation", "mean_score")]
    display_columns.extend(
      [
        (evaluating_model, f"mean_score_{suffix}")
        for evaluating_model, suffix in model_labels
      ]
    )

    x = np.arange(len(grouped))
    n_series = len(display_columns)
    if n_series == 0:
      return
    width = 0.8 / n_series
    offsets = np.arange(n_series) * width - (width * (n_series - 1) / 2)

    fig, ax = plt.subplots(figsize=(max(10, len(grouped) * 0.4), 6))
    for index, (label, column) in enumerate(display_columns):
      if column not in grouped.columns:
        continue
      _bars = ax.bar(x + offsets[index], grouped[column], width=width, label=label)
      # ax.bar_label(
      #   bars,
      #   labels=[f"{value:.2f}" for value in bars.datavalues], # type: ignore
      #   padding=2,
      # )

    ax.set_ylabel("Total mean score")
    ax.set_xlabel(group_key.replace("_", " ").title())
    ax.set_title(title)
    ax.set_xticks(x)
    ax.set_xticklabels(grouped.index, rotation=45, ha="right")
    ax.legend()
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    fig.savefig(output_dir.joinpath(filename), format="svg", bbox_inches="tight")
    plt.close(fig)

  plot_grouped_bars(
    "character",
    "Character-wise Total Mean Score by Evaluation Round",
    "test_scores_by_char.svg",
  )
  plot_grouped_bars(
    "persona_key",
    "Persona Prompt Strategy Total Mean Score by Evaluation Round",
    "test_scores_by_prompt_strat.svg",
  )
  plot_grouped_bars(
    "attack_key",
    "Attack-wise Total Mean Score by Evaluation Round",
    "test_scores_by_attack.svg",
  )

  # Correlation heatmaps
  evaluators = ["Human Evaluation"] + [model for model, _ in model_labels]
  for metric_label in ["total", "always", "never"]:
    # Filter correlation data for this metric
    filtered_data = [row for row in correlation_data if row["Metric"] == metric_label]
    if not filtered_data:
      continue
    # Create correlation matrix
    corr_matrix = pd.DataFrame(np.nan, index=evaluators, columns=evaluators)
    for row in filtered_data:
      if row["Comparison Type"] == "Human vs. Model":
        row_idx = evaluators.index("Human Evaluation")
        col_idx = evaluators.index(row["Model 2"])
        corr_matrix.iloc[row_idx, col_idx] = row["Correlation"]
        corr_matrix.iloc[col_idx, row_idx] = row["Correlation"]  # symmetric
      elif row["Comparison Type"] == "Model vs. Model":
        row_idx = evaluators.index(row["Model 1"])
        col_idx = evaluators.index(row["Model 2"])
        corr_matrix.iloc[row_idx, col_idx] = row["Correlation"]
        corr_matrix.iloc[col_idx, row_idx] = row["Correlation"]
    # Set diagonal to 1.0
    # np.fill_diagonal(corr_matrix.values, 1.0)
    # Plot heatmap
    plt.figure(figsize=(10, 8))
    sns.heatmap(
      corr_matrix, annot=True, fmt=".2f", cmap="coolwarm", cbar=True, square=True
    )
    plt.title(f"Correlation Heatmap ({metric_label} score)")
    plt.tight_layout()
    plt.savefig(
      output_dir.joinpath(f"correlation_heatmap_{metric_label}.svg"),
      format="svg",
      bbox_inches="tight",
    )
    plt.close()


main()
