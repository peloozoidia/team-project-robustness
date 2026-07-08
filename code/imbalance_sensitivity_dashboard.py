#!/usr/bin/env python3
"""
Build an imbalance sensitivity dashboard from combined_transcript_results.csv.

This companion dashboard follows the same unit of analysis as build_dashboard.py:
    one row = one unique transcript-level result.

If the input CSV still contains duplicate judge evaluations for the same transcript,
this script collapses them first by averaging score columns and keeping the first
metadata value. Raw duplicate evaluations are reported only as a KPI.

Usage from the project root:
    python code/imbalance_sensitivity_dashboard.py

The script reads:
    outputs/combined_transcript_results.csv

The script writes:
    outputs/imbalance_sensitivity_dashboard.html
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Iterable

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio


def infer_project_root() -> Path:
  """
  Find the project root from either the current working directory or this file.
  This mirrors the main dashboard behavior.
  """
  script_path = Path(__file__).resolve()
  candidates = [Path.cwd().resolve(), script_path.parent, *script_path.parents]

  for candidate in candidates:
    if (candidate / "outputs" / "combined_transcript_results.csv").exists():
      return candidate

  for candidate in candidates:
    if (candidate / "outputs").exists() or (candidate / "code").exists():
      return candidate

  return script_path.parents[1] if len(script_path.parents) > 1 else script_path.parent


PROJECT_ROOT = infer_project_root()

DEFAULT_INPUT = PROJECT_ROOT / "outputs" / "combined_transcript_results.csv"
DEFAULT_OUTPUT = PROJECT_ROOT / "outputs" / "imbalance_sensitivity_dashboard.html"

SCORE_COL = "results.test_score"
ALWAYS_SCORE_COL = "results.always_test_score"
NEVER_SCORE_COL = "results.never_test_score"

ATTACK_COL = "results.attack_key"
ATTACK_TRAIT_COL = "results.attack_trait"
TRANSCRIPT_ID_COL = "results.transcript_id"
DUPLICATE_EVAL_COUNT_COL = "duplicate_eval_count"

CHARACTER_COL = "character.name"

SCORE_MAX = 4.0
RULE_TYPE_SCORE_MAX = 2.0

SCORE_PERCENT_COL = "score_percent"
ALWAYS_PERCENT_COL = "always_score_percent"
NEVER_PERCENT_COL = "never_score_percent"

ROBUSTNESS_COLOR_SCALE = [
  [0.00, "#b84a4a"],
  [0.25, "#d98445"],
  [0.50, "#d8c96a"],
  [0.75, "#5fb3a4"],
  [1.00, "#5f8df7"],
]

DIFFERENCE_COLOR_SCALE = [
  [0.00, "#b84a4a"],
  [0.50, "#d8c96a"],
  [1.00, "#5f8df7"],
]

OPTIONAL_SCORE_COLUMNS = [
  SCORE_COL,
  ALWAYS_SCORE_COL,
  NEVER_SCORE_COL,
]

TARGET_VALUE_COLUMNS = {
  "gender": ["character.gender"],
  "ancestry": ["character.ancestry"],
  "race": ["character.ancestry"],
  "age": ["character.age"],
  "role": ["character.role"],
  "occupation": ["character.role"],
  "role_detail": ["character.role_detail_label", "character.role_detail"],
  "role detail": ["character.role_detail_label", "character.role_detail"],
  "specification": ["character.role_detail_label", "character.role_detail"],
  "ideal": ["character.ideal"],
  "ideal_axis": ["character.ideal_axis"],
  "ideal axis": ["character.ideal_axis"],
  "alignment": ["character.alignment"],
  "flaw": ["character.flaw"],
}

DASHBOARD_CSS = ":root {\n      --bg: #0b1020;\n      --panel: #121933;\n      --panel-2: #0f1530;\n      --border: rgba(255,255,255,0.08);\n      --text: #ecf1ff;\n      --muted: #a8b2d1;\n      --accent: #7aa2ff;\n      --accent-2: #9ec0ff;\n      --shadow: 0 16px 40px rgba(0,0,0,0.25);\n      --radius: 20px;\n    }\n    * { box-sizing: border-box; }\n    html { scroll-behavior: smooth; }\n    body {\n      margin: 0;\n      font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;\n      background: linear-gradient(180deg, #0a0f1d 0%, #111731 100%);\n      color: var(--text);\n    }\n    .app {\n      display: grid;\n      grid-template-columns: 260px 1fr;\n      min-height: 100vh;\n    }\n    .sidebar {\n      position: sticky;\n      top: 0;\n      height: 100vh;\n      overflow: auto;\n      border-right: 1px solid var(--border);\n      background: rgba(9, 13, 28, 0.96);\n      padding: 18px 16px 28px;\n    }\n    .sidebar h2 { margin: 0 0 8px; font-size: 18px; }\n    .small { color: var(--muted); font-size: 12px; margin-bottom: 14px; line-height: 1.45; }\n    .toc {\n      border: 1px solid var(--border);\n      border-radius: 14px;\n      background: rgba(255,255,255,0.02);\n      padding: 10px 14px 12px;\n    }\n    .toc a {\n      display: block;\n      color: var(--accent-2);\n      text-decoration: none;\n      font-size: 13px;\n      line-height: 1.5;\n      padding: 5px 0;\n    }\n    .sidebar-actions {\n      position: sticky;\n      bottom: 0;\n      background: linear-gradient(180deg, rgba(9,13,28,0) 0%, rgba(9,13,28,0.98) 24%);\n      padding-top: 12px;\n      margin-top: 14px;\n    }\n    .sidebar-actions button {\n      width: 100%;\n      border: 1px solid var(--border);\n      background: var(--panel);\n      color: var(--text);\n      padding: 12px 14px;\n      border-radius: 12px;\n      cursor: pointer;\n      margin-top: 8px;\n      font-weight: 600;\n    }\n    .main { padding: 24px 30px 36px; max-width: 1760px; width: 100%; margin: 0 auto; }\n    .hero {\n      display: grid;\n      grid-template-columns: 1.8fr 1.2fr;\n      gap: 14px;\n      margin-bottom: 14px;\n      align-items: start;\n    }\n    .card {\n      background: linear-gradient(180deg, rgba(255,255,255,0.028), rgba(255,255,255,0.012));\n      border: 1px solid var(--border);\n      border-radius: 18px;\n      padding: 16px 18px;\n      box-shadow: 0 8px 24px rgba(0,0,0,0.16);\n      backdrop-filter: blur(8px);\n    }\n    h1 { font-size: 28px; line-height: 1.15; margin: 0 0 8px; letter-spacing: -0.02em; }\n    .subtitle { color: var(--muted); line-height: 1.5; margin: 0; font-size: 14px; max-width: 72ch; }\n    .kpis {\n      display: grid;\n      grid-template-columns: repeat(3, minmax(0, 1fr));\n      gap: 10px;\n      height: 100%;\n      align-content: start;\n    }\n    .kpi {\n      background: var(--panel-2);\n      border: 1px solid var(--border);\n      border-radius: 14px;\n      padding: 12px 13px;\n      min-height: 84px;\n    }\n    .kpi .label {\n      color: var(--muted);\n      font-size: 11px;\n      text-transform: uppercase;\n      letter-spacing: 0.07em;\n    }\n    .kpi .value {\n      font-size: 24px;\n      font-weight: 700;\n      margin-top: 8px;\n      line-height: 1.15;\n    }\n    .kpi .value.text-value {\n      font-size: 17px;\n      line-height: 1.25;\n      overflow-wrap: anywhere;\n    }\n    .methodology-grid {\n      display: grid;\n      grid-template-columns: repeat(3, minmax(0, 1fr));\n      gap: 12px;\n    }\n    .methodology-item {\n      border: 1px solid rgba(255,255,255,0.07);\n      background: rgba(255,255,255,0.018);\n      border-radius: 14px;\n      padding: 14px;\n    }\n    .methodology-label {\n      color: var(--accent-2);\n      font-weight: 700;\n      font-size: 13px;\n      margin-bottom: 8px;\n      text-transform: uppercase;\n      letter-spacing: 0.05em;\n    }\n    .methodology-item p {\n      color: #d9e3ff;\n      margin: 0;\n      line-height: 1.5;\n      font-size: 13px;\n    }\n    .table-intro {\n      color: var(--muted);\n      font-size: 13px;\n      line-height: 1.5;\n      margin-bottom: 10px;\n    }\n    .family {\n      margin: 18px 0;\n      border: 1px solid var(--border);\n      border-radius: 20px;\n      overflow: hidden;\n      background: rgba(255,255,255,0.02);\n      box-shadow: var(--shadow);\n    }\n    .family-header {\n      padding: 16px 18px;\n      font-size: 22px;\n      font-weight: 700;\n      letter-spacing: -0.01em;\n      cursor: pointer;\n      background: rgba(255,255,255,0.03);\n      display: flex;\n      justify-content: space-between;\n      align-items: center;\n    }\n    .family-subtitle {\n      color: var(--muted);\n      font-size: 13px;\n      font-weight: 400;\n      margin-top: 6px;\n      max-width: 88ch;\n    }\n    .family-content { display: none; padding: 18px; }\n    .family.open .family-content { display: block; }\n    .grid {\n      display: grid;\n      grid-template-columns: repeat(12, 1fr);\n      gap: 18px;\n    }\n    .graph-card {\n      background: linear-gradient(180deg, rgba(255,255,255,0.018), rgba(255,255,255,0.009));\n      border: 1px solid var(--border);\n      border-radius: 18px;\n      overflow: hidden;\n      grid-column: span 12;\n      box-shadow: 0 8px 22px rgba(0,0,0,0.14);\n    }\n    .graph-header {\n      padding: 14px 16px;\n      cursor: pointer;\n      display: flex;\n      align-items: center;\n      justify-content: space-between;\n      gap: 12px;\n      background: rgba(255,255,255,0.025);\n    }\n    .graph-header h3 { margin: 0; font-size: 18px; line-height: 1.2; letter-spacing: -0.01em; }\n    .graph-actions {\n      display: inline-flex;\n      align-items: center;\n      gap: 8px;\n      flex-shrink: 0;\n    }\n    .graph-title-block {\n      min-width: 0;\n      flex: 1 1 auto;\n    }\n    .export-button {\n      border: 1px solid rgba(255,255,255,0.10);\n      background: rgba(255,255,255,0.04);\n      color: var(--text);\n      width: 36px;\n      height: 36px;\n      padding: 0;\n      border-radius: 10px;\n      cursor: pointer;\n      display: inline-flex;\n      align-items: center;\n      justify-content: center;\n    }\n    .export-button:hover {\n      border-color: rgba(255,255,255,0.22);\n      background: rgba(255,255,255,0.08);\n    }\n    .export-icon {\n      width: 18px;\n      height: 18px;\n      display: block;\n      object-fit: contain;\n      border-radius: 4px;\n    }\n    .note { color: var(--muted); font-size: 12.5px; line-height: 1.45; margin-top: 5px; max-width: 78ch; }\n    .graph-content { display: none; padding: 14px 16px 16px; }\n    .graph-card.open .graph-content { display: block; }\n    .badge {\n      display: inline-flex;\n      align-items: center;\n      justify-content: center;\n      min-width: 24px;\n      height: 24px;\n      border-radius: 999px;\n      border: 1px solid var(--border);\n      background: rgba(255,255,255,0.03);\n      font-size: 12px;\n      color: var(--muted);\n      padding: 0 8px;\n    }\n    .table-wrap {\n      overflow: auto;\n      border: 1px solid var(--border);\n      border-radius: 14px;\n      background: rgba(255,255,255,0.015);\n    }\n    .data-table {\n      width: 100%;\n      border-collapse: collapse;\n      font-size: 13px;\n      min-width: 980px;\n    }\n    .data-table th,\n    .data-table td {\n      padding: 10px 12px;\n      border-bottom: 1px solid rgba(255,255,255,0.06);\n      text-align: left;\n      vertical-align: top;\n    }\n    .data-table th {\n      color: var(--text);\n      background: rgba(255,255,255,0.04);\n      position: sticky;\n      top: 0;\n      z-index: 1;\n    }\n    .data-table td {\n      color: #d9e3ff;\n    }\n    .data-table tr:hover td {\n      background: rgba(255,255,255,0.03);\n    }\n    .footer {\n      color: var(--muted);\n      font-size: 12px;\n      margin-top: 24px;\n      text-align: center;\n    }\n    @media (max-width: 1200px) {\n      .app { grid-template-columns: 1fr; }\n      .sidebar {\n        position: relative;\n        height: auto;\n        border-right: 0;\n        border-bottom: 1px solid var(--border);\n      }\n      .hero { grid-template-columns: 1fr; }\n      .kpis { grid-template-columns: repeat(2, minmax(0, 1fr)); }\n      .methodology-grid { grid-template-columns: 1fr; }\n    }\n\n    .summary-table {\n      width: 100%;\n      border-collapse: collapse;\n      font-size: 13px;\n      min-width: 980px;\n    }\n    .summary-table th,\n    .summary-table td {\n      padding: 10px 12px;\n      border-bottom: 1px solid rgba(255,255,255,0.06);\n      text-align: left;\n      vertical-align: top;\n    }\n    .summary-table th {\n      color: var(--text);\n      background: rgba(255,255,255,0.04);\n      position: sticky;\n      top: 0;\n      z-index: 1;\n    }\n    .summary-table td {\n      color: #d9e3ff;\n    }\n    .summary-table tr:hover td {\n      background: rgba(255,255,255,0.03);\n    }\n    .plot-wrap {\n      width: 100%;\n      min-height: 420px;\n    }\n"

DASHBOARD_JS = '\n<script>\n  function toggleFamily(el) {\n    el.classList.toggle("open");\n  }\n\n  function toggleGraph(el) {\n    el.classList.toggle("open");\n  }\n\n  function collapseAll() {\n    document.querySelectorAll(".family, .graph-card").forEach(function(el) {\n      el.classList.remove("open");\n    });\n  }\n\n  function expandAll() {\n    document.querySelectorAll(".family, .graph-card").forEach(function(el) {\n      el.classList.add("open");\n    });\n  }\n</script>\n'


def require_columns(df: pd.DataFrame, columns: Iterable[str]) -> None:
  missing = [col for col in columns if col not in df.columns]
  if missing:
    raise ValueError(
      "Input CSV is missing required columns:\n"
      + "\n".join(f"  - {col}" for col in missing)
    )


def is_missing(value: object) -> bool:
  if value is None:
    return True

  if isinstance(value, float) and math.isnan(value):
    return True

  text = str(value).strip().lower()
  return text in {"", "nan", "none", "nat", "<na>"}


def normalize_text(value: object) -> str:
  if is_missing(value):
    return "Unknown"

  return str(value).strip()


def to_float(value: object) -> float | None:
  if is_missing(value):
    return None

  try:
    return float(str(value))
  except (TypeError, ValueError):
    return None


def format_number(value: object, digits: int = 2) -> str:
  number = to_float(value)
  if number is None:
    return ""

  return f"{number:.{digits}f}"


def format_percent(value: object, digits: int = 1) -> str:
  number = to_float(value)
  if number is None:
    return ""

  return f"{number:.{digits}f}%"


def format_signed_number(value: object, digits: int = 1) -> str:
  number = to_float(value)
  if number is None:
    return ""

  return f"{number:+.{digits}f}"


def format_int(value: object, missing: str = "") -> str:
  number = to_float(value)
  if number is None:
    return missing

  return str(int(number))


def score_to_percent(series: pd.Series, max_score: float) -> pd.Series:
  return (pd.to_numeric(series, errors="coerce").clip(0, max_score) / max_score) * 100


def collapse_to_transcript_level(
  df: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, int]]:
  """
  Return transcript-level data and basic count metadata.

  Cases handled:
  - Already collapsed CSV:
      one row per transcript, possibly with duplicate_eval_count.
  - Raw duplicate CSV:
      several rows per results.transcript_id; scores are averaged first.
  """
  input_rows = len(df)

  if DUPLICATE_EVAL_COUNT_COL in df.columns:
    duplicate_counts = pd.to_numeric(
      df[DUPLICATE_EVAL_COUNT_COL],
      errors="coerce",
    ).fillna(1)
    raw_evaluations_loaded = int(duplicate_counts.sum())
  else:
    raw_evaluations_loaded = input_rows
    duplicate_counts = pd.Series([1] * input_rows, index=df.index)

  df = df.copy()
  df[DUPLICATE_EVAL_COUNT_COL] = duplicate_counts.astype(int)

  if TRANSCRIPT_ID_COL not in df.columns:
    metadata = {
      "input_rows": input_rows,
      "unique_transcripts": len(df),
      "raw_evaluations_loaded": raw_evaluations_loaded,
    }
    return df, metadata

  if not df[TRANSCRIPT_ID_COL].duplicated().any():
    metadata = {
      "input_rows": input_rows,
      "unique_transcripts": len(df),
      "raw_evaluations_loaded": raw_evaluations_loaded,
    }
    return df, metadata

  score_cols = [col for col in OPTIONAL_SCORE_COLUMNS if col in df.columns]
  metadata_cols = [
    col
    for col in df.columns
    if col not in score_cols and col != DUPLICATE_EVAL_COUNT_COL
  ]

  agg_spec = {col: "first" for col in metadata_cols}
  agg_spec.update({col: "mean" for col in score_cols})
  agg_spec[DUPLICATE_EVAL_COUNT_COL] = "sum"

  collapsed = (
    df.groupby(TRANSCRIPT_ID_COL, as_index=False, dropna=False)
    .agg(agg_spec)
    .reset_index(drop=True)
  )

  metadata = {
    "input_rows": input_rows,
    "unique_transcripts": len(collapsed),
    "raw_evaluations_loaded": raw_evaluations_loaded,
  }

  return collapsed, metadata


def read_and_prepare_data(input_path: Path) -> tuple[pd.DataFrame, dict[str, int]]:
  df = pd.read_csv(input_path)

  require_columns(
    df,
    [
      ATTACK_COL,
      ATTACK_TRAIT_COL,
      SCORE_COL,
    ],
  )

  df, metadata = collapse_to_transcript_level(df)

  for col in OPTIONAL_SCORE_COLUMNS:
    if col in df.columns:
      df[col] = pd.to_numeric(df[col], errors="coerce")

  df = df.dropna(subset=[SCORE_COL]).copy()

  df[SCORE_PERCENT_COL] = score_to_percent(df[SCORE_COL], SCORE_MAX)

  if ALWAYS_SCORE_COL in df.columns:
    df[ALWAYS_PERCENT_COL] = score_to_percent(df[ALWAYS_SCORE_COL], RULE_TYPE_SCORE_MAX)

  if NEVER_SCORE_COL in df.columns:
    df[NEVER_PERCENT_COL] = score_to_percent(df[NEVER_SCORE_COL], RULE_TYPE_SCORE_MAX)

  text_cols = [
    ATTACK_COL,
    ATTACK_TRAIT_COL,
    CHARACTER_COL,
    "character.gender",
    "character.alignment",
    "character.ancestry",
    "character.age",
    "character.role",
    "character.role_detail_label",
    "character.role_detail",
    "character.ideal",
    "character.ideal_axis",
    "character.flaw",
  ]

  for col in text_cols:
    if col in df.columns:
      df[col] = df[col].map(normalize_text)

  df = add_target_value_columns(df)

  metadata["unique_transcripts"] = len(df)

  return df, metadata


def add_target_value_columns(df: pd.DataFrame) -> pd.DataFrame:
  """
  Add:
  - target_value: concrete value of the attacked trait
  - macro_unit: attacked trait + concrete value
  """
  df = df.copy()

  target_values: list[str] = []

  for _, row in df.iterrows():
    trait = normalize_text(row.get(ATTACK_TRAIT_COL)).lower()
    candidates = TARGET_VALUE_COLUMNS.get(trait, [])

    value = "Unknown"

    for col in candidates:
      if col in df.columns:
        raw_value = row.get(col)
        if not is_missing(raw_value):
          value = normalize_text(raw_value)
          break

    target_values.append(value)

  df["target_value"] = target_values
  df["macro_unit"] = (
    df[ATTACK_TRAIT_COL].map(normalize_text)
    + ": "
    + df["target_value"].map(normalize_text)
  )

  return df


def summarize_raw_vs_macro(
  df: pd.DataFrame,
  group_cols: list[str],
  score_col: str,
  macro_unit_col: str,
) -> pd.DataFrame:
  """
  Raw score:
      Mean over transcript-level rows.

  Macro score:
      First mean within each macro unit, then mean over macro units.
  """
  raw = (
    df.groupby(group_cols, dropna=False)
    .agg(
      raw_score=(score_col, "mean"),
      raw_median=(score_col, "median"),
      n_transcripts=(score_col, "size"),
      raw_evaluations=(DUPLICATE_EVAL_COUNT_COL, "sum"),
    )
    .reset_index()
  )

  unit_means = (
    df.groupby(group_cols + [macro_unit_col], dropna=False)
    .agg(
      unit_score=(score_col, "mean"),
      unit_transcripts=(score_col, "size"),
    )
    .reset_index()
  )

  macro = (
    unit_means.groupby(group_cols, dropna=False)
    .agg(
      macro_score=("unit_score", "mean"),
      macro_units=("unit_score", "size"),
      min_unit_n=("unit_transcripts", "min"),
      max_unit_n=("unit_transcripts", "max"),
    )
    .reset_index()
  )

  out = raw.merge(macro, on=group_cols, how="left")
  out["score_difference"] = out["macro_score"] - out["raw_score"]
  out["abs_difference"] = out["score_difference"].abs()

  return out


def add_rank_changes(df: pd.DataFrame) -> pd.DataFrame:
  """
  Higher robustness score is treated as better.
  Rank 1 = highest robustness.
  Positive rank_change means the item moved up after macro-averaging.
  """
  df = df.copy()

  df["raw_rank"] = df["raw_score"].rank(method="min", ascending=False)
  df["macro_rank"] = df["macro_score"].rank(method="min", ascending=False)

  df["rank_change"] = df["raw_rank"] - df["macro_rank"]
  df["abs_rank_change"] = df["rank_change"].abs()

  return df


def style_fig(fig: go.Figure, title: str, height: int) -> go.Figure:
  fig.update_layout(
    title=title,
    height=height,
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font={"color": "#ecf1ff"},
    margin={"t": 60, "l": 70, "r": 35, "b": 80},
    legend={
      "bgcolor": "rgba(0,0,0,0)",
      "bordercolor": "rgba(255,255,255,0.08)",
      "borderwidth": 1,
    },
  )
  fig.update_xaxes(
    gridcolor="rgba(255,255,255,0.08)",
    zerolinecolor="rgba(255,255,255,0.08)",
  )
  fig.update_yaxes(
    gridcolor="rgba(255,255,255,0.08)",
    zerolinecolor="rgba(255,255,255,0.08)",
  )
  return fig


def make_raw_macro_attack_plot(summary: pd.DataFrame) -> go.Figure:
  data = summary.sort_values("raw_score", ascending=True)

  custom_raw = list(
    zip(
      data["n_transcripts"],
      data["raw_evaluations"],
      data["macro_units"],
      data["score_difference"],
    )
  )

  fig = go.Figure()

  fig.add_trace(
    go.Bar(
      name="Raw observed score",
      x=data["raw_score"],
      y=data[ATTACK_COL],
      orientation="h",
      customdata=custom_raw,
      hovertemplate=(
        "<b>%{y}</b><br>"
        "Raw score: %{x:.1f}%<br>"
        "Unique transcripts: %{customdata[0]}<br>"
        "Raw evaluations: %{customdata[1]}<br>"
        "Macro units: %{customdata[2]}<br>"
        "Macro - raw: %{customdata[3]:+.1f} pp"
        "<extra></extra>"
      ),
    )
  )

  fig.add_trace(
    go.Bar(
      name="Macro-averaged score",
      x=data["macro_score"],
      y=data[ATTACK_COL],
      orientation="h",
      customdata=custom_raw,
      hovertemplate=(
        "<b>%{y}</b><br>"
        "Macro score: %{x:.1f}%<br>"
        "Unique transcripts: %{customdata[0]}<br>"
        "Raw evaluations: %{customdata[1]}<br>"
        "Macro units: %{customdata[2]}<br>"
        "Macro - raw: %{customdata[3]:+.1f} pp"
        "<extra></extra>"
      ),
    )
  )

  fig.update_layout(
    barmode="group",
    legend_title="Score type",
  )
  fig.update_xaxes(title="Robustness score (%)", range=[0, 100], ticksuffix="%")
  fig.update_yaxes(title="Attack strategy")

  return style_fig(
    fig,
    title="Raw vs Macro-Averaged Robustness by Attack Strategy",
    height=max(650, 26 * len(data)),
  )


def make_attack_difference_plot(summary: pd.DataFrame) -> go.Figure:
  data = summary.sort_values("score_difference", ascending=True)

  custom = list(
    zip(
      data["raw_score"],
      data["macro_score"],
      data["n_transcripts"],
      data["raw_evaluations"],
      data["macro_units"],
    )
  )

  fig = go.Figure()

  fig.add_trace(
    go.Bar(
      x=data["score_difference"],
      y=data[ATTACK_COL],
      orientation="h",
      customdata=custom,
      hovertemplate=(
        "<b>%{y}</b><br>"
        "Difference: %{x:+.1f} pp<br>"
        "Raw score: %{customdata[0]:.1f}%<br>"
        "Macro score: %{customdata[1]:.1f}%<br>"
        "Unique transcripts: %{customdata[2]}<br>"
        "Raw evaluations: %{customdata[3]}<br>"
        "Macro units: %{customdata[4]}"
        "<extra></extra>"
      ),
    )
  )

  fig.add_vline(x=0, line_width=1, line_dash="dash")

  fig.update_xaxes(title="Macro-averaged score minus raw score, percentage points")
  fig.update_yaxes(title="Attack strategy")

  return style_fig(
    fig,
    title="Correction Effect by Attack Strategy",
    height=max(650, 26 * len(data)),
  )


def make_rank_change_plot(summary: pd.DataFrame) -> go.Figure:
  data = summary.sort_values("rank_change", ascending=True)

  custom = list(
    zip(
      data["raw_rank"],
      data["macro_rank"],
      data["raw_score"],
      data["macro_score"],
      data["n_transcripts"],
      data["raw_evaluations"],
    )
  )

  fig = go.Figure()

  fig.add_trace(
    go.Bar(
      x=data["rank_change"],
      y=data[ATTACK_COL],
      orientation="h",
      customdata=custom,
      hovertemplate=(
        "<b>%{y}</b><br>"
        "Rank change: %{x:+.0f}<br>"
        "Raw rank: %{customdata[0]:.0f}<br>"
        "Macro rank: %{customdata[1]:.0f}<br>"
        "Raw score: %{customdata[2]:.1f}%<br>"
        "Macro score: %{customdata[3]:.1f}%<br>"
        "Unique transcripts: %{customdata[4]}<br>"
        "Raw evaluations: %{customdata[5]}"
        "<extra></extra>"
      ),
    )
  )

  fig.add_vline(x=0, line_width=1, line_dash="dash")
  fig.update_xaxes(
    title="Raw rank - macro rank; positive means moved up after correction"
  )
  fig.update_yaxes(title="Attack strategy")

  return style_fig(
    fig,
    title="Attack Strategy Rank Changes After Macro-Averaging",
    height=max(650, 26 * len(data)),
  )


def make_target_trait_plot(summary: pd.DataFrame) -> go.Figure:
  data = summary.sort_values("raw_score", ascending=True)

  custom = list(
    zip(
      data["n_transcripts"],
      data["raw_evaluations"],
      data["macro_units"],
      data["score_difference"],
    )
  )

  fig = go.Figure()

  fig.add_trace(
    go.Bar(
      name="Raw observed score",
      x=data["raw_score"],
      y=data[ATTACK_TRAIT_COL],
      orientation="h",
      customdata=custom,
      hovertemplate=(
        "<b>%{y}</b><br>"
        "Raw score: %{x:.1f}%<br>"
        "Unique transcripts: %{customdata[0]}<br>"
        "Raw evaluations: %{customdata[1]}<br>"
        "Macro units: %{customdata[2]}<br>"
        "Macro - raw: %{customdata[3]:+.1f} pp"
        "<extra></extra>"
      ),
    )
  )

  fig.add_trace(
    go.Bar(
      name="Macro-averaged score",
      x=data["macro_score"],
      y=data[ATTACK_TRAIT_COL],
      orientation="h",
      customdata=custom,
      hovertemplate=(
        "<b>%{y}</b><br>"
        "Macro score: %{x:.1f}%<br>"
        "Unique transcripts: %{customdata[0]}<br>"
        "Raw evaluations: %{customdata[1]}<br>"
        "Macro units: %{customdata[2]}<br>"
        "Macro - raw: %{customdata[3]:+.1f} pp"
        "<extra></extra>"
      ),
    )
  )

  fig.update_layout(
    barmode="group",
    legend_title="Score type",
  )
  fig.update_xaxes(title="Robustness score (%)", range=[0, 100], ticksuffix="%")
  fig.update_yaxes(title="Target trait")

  return style_fig(
    fig,
    title="Raw vs Macro-Averaged Robustness by Target Trait",
    height=max(450, 90 * len(data)),
  )


def make_raw_vs_macro_scatter(summary: pd.DataFrame) -> go.Figure:
  custom = list(
    zip(
      summary["score_difference"],
      summary["rank_change"],
      summary["n_transcripts"],
      summary["raw_evaluations"],
      summary["macro_units"],
    )
  )

  fig = go.Figure()

  fig.add_trace(
    go.Scatter(
      x=summary["raw_score"],
      y=summary["macro_score"],
      mode="markers",
      text=summary[ATTACK_COL],
      customdata=custom,
      marker={
        "size": 12,
        "color": summary["score_difference"],
        "colorscale": DIFFERENCE_COLOR_SCALE,
        "colorbar": {"title": "Macro - raw"},
        "line": {"width": 1, "color": "rgba(255,255,255,0.45)"},
      },
      hovertemplate=(
        "<b>%{text}</b><br>"
        "Raw score: %{x:.1f}%<br>"
        "Macro score: %{y:.1f}%<br>"
        "Macro - raw: %{customdata[0]:+.1f} pp<br>"
        "Rank change: %{customdata[1]:+.0f}<br>"
        "Unique transcripts: %{customdata[2]}<br>"
        "Raw evaluations: %{customdata[3]}<br>"
        "Macro units: %{customdata[4]}"
        "<extra></extra>"
      ),
    )
  )

  fig.add_trace(
    go.Scatter(
      x=[0, 100],
      y=[0, 100],
      mode="lines",
      name="No difference",
      hoverinfo="skip",
      line={"dash": "dash"},
    )
  )

  fig.update_xaxes(title="Raw observed score (%)", range=[0, 100], ticksuffix="%")
  fig.update_yaxes(title="Macro-averaged score (%)", range=[0, 100], ticksuffix="%")
  fig.update_layout(showlegend=False)

  return style_fig(fig, title="Raw vs Macro-Averaged Attack Scores", height=650)


def make_attack_trait_difference_heatmap(cell_summary: pd.DataFrame) -> go.Figure:
  pivot = cell_summary.pivot(
    index=ATTACK_COL,
    columns=ATTACK_TRAIT_COL,
    values="score_difference",
  )

  n_pivot = cell_summary.pivot(
    index=ATTACK_COL,
    columns=ATTACK_TRAIT_COL,
    values="n_transcripts",
  )

  raw_eval_pivot = cell_summary.pivot(
    index=ATTACK_COL,
    columns=ATTACK_TRAIT_COL,
    values="raw_evaluations",
  )

  hover_text: list[list[str]] = []

  for attack in pivot.index:
    row = []
    for trait in pivot.columns:
      diff = pivot.loc[attack, trait]
      n_value = n_pivot.loc[attack, trait]
      raw_eval_value = raw_eval_pivot.loc[attack, trait]

      if is_missing(diff):
        row.append("No data")
      else:
        row.append(
          f"Attack: {attack}<br>"
          f"Target trait: {trait}<br>"
          f"Macro - raw: {format_signed_number(diff, 1)} pp<br>"
          f"Unique transcripts: {format_int(n_value, missing='unknown')}<br>"
          f"Raw evaluations: {format_int(raw_eval_value, missing='unknown')}"
        )
    hover_text.append(row)

  fig = go.Figure(
    data=go.Heatmap(
      z=pivot.values,
      x=pivot.columns,
      y=pivot.index,
      text=hover_text,
      hovertemplate="%{text}<extra></extra>",
      colorscale=DIFFERENCE_COLOR_SCALE,
      zmid=0,
      colorbar={"title": "Macro - raw"},
    )
  )

  fig.update_xaxes(title="Target trait")
  fig.update_yaxes(title="Attack strategy")

  return style_fig(
    fig,
    title="Correction Effect Heatmap: Attack Strategy × Target Trait",
    height=max(650, 24 * len(pivot.index)),
  )


def make_summary_table_html(summary: pd.DataFrame) -> str:
  table = summary.sort_values("abs_rank_change", ascending=False).copy()

  table = table[
    [
      ATTACK_COL,
      "raw_score",
      "macro_score",
      "score_difference",
      "raw_rank",
      "macro_rank",
      "rank_change",
      "n_transcripts",
      "raw_evaluations",
      "macro_units",
      "min_unit_n",
    ]
  ]

  table = table.rename(
    columns={
      ATTACK_COL: "Attack",
      "raw_score": "Raw score",
      "macro_score": "Macro score",
      "score_difference": "Macro - raw",
      "raw_rank": "Raw rank",
      "macro_rank": "Macro rank",
      "rank_change": "Rank change",
      "n_transcripts": "Unique transcripts",
      "raw_evaluations": "Raw evaluations",
      "macro_units": "Macro units",
      "min_unit_n": "Smallest unit n",
    }
  )

  for col in ["Raw score", "Macro score"]:
    table[col] = table[col].map(lambda x: format_percent(x, 1))

  table["Macro - raw"] = table["Macro - raw"].map(
    lambda x: f"{format_signed_number(x, 1)} pp"
  )

  for col in [
    "Raw rank",
    "Macro rank",
    "Rank change",
    "Unique transcripts",
    "Raw evaluations",
    "Macro units",
    "Smallest unit n",
  ]:
    table[col] = table[col].map(format_int)

  return table.to_html(index=False, classes="summary-table", escape=True)


def make_low_count_table_html(summary: pd.DataFrame, threshold: int = 10) -> str:
  low = summary[summary["min_unit_n"] < threshold].copy()

  if low.empty:
    return f"<p>No attack strategy has a macro unit below n &lt; {threshold}.</p>"

  low = low.sort_values(["min_unit_n", "n_transcripts"], ascending=[True, True])

  low = low[
    [
      ATTACK_COL,
      "n_transcripts",
      "raw_evaluations",
      "macro_units",
      "min_unit_n",
      "max_unit_n",
      "raw_score",
      "macro_score",
      "score_difference",
    ]
  ]

  low = low.rename(
    columns={
      ATTACK_COL: "Attack",
      "n_transcripts": "Unique transcripts",
      "raw_evaluations": "Raw evaluations",
      "macro_units": "Macro units",
      "min_unit_n": "Smallest unit n",
      "max_unit_n": "Largest unit n",
      "raw_score": "Raw score",
      "macro_score": "Macro score",
      "score_difference": "Macro - raw",
    }
  )

  for col in ["Raw score", "Macro score"]:
    low[col] = low[col].map(lambda x: format_percent(x, 1))

  low["Macro - raw"] = low["Macro - raw"].map(
    lambda x: f"{format_signed_number(x, 1)} pp"
  )

  for col in [
    "Unique transcripts",
    "Raw evaluations",
    "Macro units",
    "Smallest unit n",
    "Largest unit n",
  ]:
    low[col] = low[col].map(format_int)

  return low.to_html(index=False, classes="summary-table", escape=True)


def fig_html(fig: go.Figure, include_plotlyjs: bool = False) -> str:
  return pio.to_html(
    fig,
    full_html=False,
    include_plotlyjs=include_plotlyjs,
    config={
      "displayModeBar": True,
      "responsive": True,
      "scrollZoom": True,
      "displaylogo": False,
    },
  )


def build_html(
  df: pd.DataFrame,
  metadata: dict[str, int],
  attack_summary: pd.DataFrame,
  target_summary: pd.DataFrame,
  cell_summary: pd.DataFrame,
  output_path: Path,
  score_col: str,
  low_count_threshold: int,
) -> str:
  unique_transcripts = metadata["unique_transcripts"]
  raw_evaluations_loaded = metadata["raw_evaluations_loaded"]
  input_rows = metadata["input_rows"]

  unique_attacks = df[ATTACK_COL].nunique(dropna=True)
  unique_target_traits = df[ATTACK_TRAIT_COL].nunique(dropna=True)
  avg_raw_score = attack_summary["raw_score"].mean()
  avg_macro_score = attack_summary["macro_score"].mean()
  max_rank_change = attack_summary["abs_rank_change"].max()

  figs = [
    make_raw_vs_macro_scatter(attack_summary),
    make_raw_macro_attack_plot(attack_summary),
    make_attack_difference_plot(attack_summary),
    make_rank_change_plot(attack_summary),
    make_target_trait_plot(target_summary),
    make_attack_trait_difference_heatmap(cell_summary),
  ]

  figs_html = [
    fig_html(fig, include_plotlyjs=(index == 0)) for index, fig in enumerate(figs)
  ]

  rank_table_html = make_summary_table_html(attack_summary)
  low_count_table_html = make_low_count_table_html(
    attack_summary,
    threshold=low_count_threshold,
  )

  html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Imbalance Sensitivity Dashboard</title>
  <style>
{DASHBOARD_CSS}
  </style>
</head>

<body>
  <div class="app">
    <aside class="sidebar">
      <h2>Table of contents</h2>
      <div class="small">
        Companion dashboard for the main robustness evaluation. All plots use transcript-level rows.
        Raw duplicate evaluations are shown only as a count.
      </div>

      <div class="toc">
        <a href="#executive-summary">Executive Summary</a>
        <a href="#attack-level-sensitivity">Attack-Level Sensitivity</a>
        <a href="#rank-changes">Rank Changes</a>
        <a href="#trait-level-sensitivity">Trait-Level Sensitivity</a>
        <a href="#interaction-sensitivity">Interaction Sensitivity</a>
        <a href="#low-count-warnings">Low-Count Warnings</a>
      </div>

      <div class="sidebar-actions">
        <button onclick="collapseAll()">Collapse all</button>
        <button onclick="expandAll()">Expand all</button>
      </div>
    </aside>

    <main class="main">
      <div class="hero">
        <div class="card">
          <h1>Imbalance Sensitivity Dashboard</h1>
          <p class="subtitle">
            This dashboard compares raw observed robustness scores with macro-averaged scores.
            It uses the same analysis unit as the main dashboard: one row per unique transcript.
            If the input CSV contains repeated judge evaluations, those rows are collapsed first.
            Scores are shown as percentages, matching the main dashboard.
          </p>
        </div>

        <div class="kpis">
          <div class="kpi"><div class="label">Unique transcripts analyzed</div><div class="value">{unique_transcripts:,}</div></div>
          <div class="kpi"><div class="label">Raw evaluations loaded</div><div class="value">{raw_evaluations_loaded:,}</div></div>
          <div class="kpi"><div class="label">Input CSV rows</div><div class="value">{input_rows:,}</div></div>
          <div class="kpi"><div class="label">Attack strategies</div><div class="value">{unique_attacks:,}</div></div>
          <div class="kpi"><div class="label">Target traits</div><div class="value">{unique_target_traits:,}</div></div>
          <div class="kpi"><div class="label">Avg raw robustness</div><div class="value">{avg_raw_score:.1f}%</div></div>
          <div class="kpi"><div class="label">Avg macro robustness</div><div class="value">{avg_macro_score:.1f}%</div></div>
          <div class="kpi"><div class="label">Max rank change</div><div class="value">{max_rank_change:.0f}</div></div>
        </div>
      </div>

      <section class="family open" id="executive-summary">
        <div class="family-header" onclick="toggleFamily(this.parentElement)">
          <div>
            Executive Summary
            <div class="family-subtitle">
              What the correction means and how to interpret the dashboard.
            </div>
          </div>
          <span class="badge">2</span>
        </div>

        <div class="family-content">
          <div class="grid">
            <div class="graph-card open" id="how-to-read-this-dashboard">
              <div class="graph-header" onclick="toggleGraph(this.parentElement)">
                <div class="graph-title-block">
                  <h3>How to Read This Dashboard</h3>
                  <div class="note">Definitions for raw scores, macro-averaged scores, differences, and rank changes.</div>
                </div>
                <div class="graph-actions" onclick="event.stopPropagation()">
                  <span class="chevron">▾</span>
                </div>
              </div>

              <div class="graph-content">
                <div class="methodology-grid">
                  <div class="methodology-item">
                    <div class="methodology-label">Analysis Unit</div>
                    <p>All plots use unique transcript-level rows. Duplicate judge evaluations are averaged before analysis.</p>
                  </div>
                  <div class="methodology-item">
                    <div class="methodology-label">Raw Score</div>
                    <p>Simple mean over transcript-level rows. This reflects the observed sample distribution.</p>
                  </div>
                  <div class="methodology-item">
                    <div class="methodology-label">Macro-Averaged Score</div>
                    <p>First average within each attacked trait value, then average those values equally.</p>
                  </div>
                  <div class="methodology-item">
                    <div class="methodology-label">Difference</div>
                    <p><strong>Macro - raw</strong>, shown in percentage points. Values near zero are stable.</p>
                  </div>
                  <div class="methodology-item">
                    <div class="methodology-label">Rank Change</div>
                    <p>Positive means an attack moved up after correction. Negative means it moved down.</p>
                  </div>
                  <div class="methodology-item">
                    <div class="methodology-label">Low-Count Warning</div>
                    <p>Warnings are based on unique transcripts, not repeated raw judge evaluations.</p>
                  </div>
                </div>
              </div>
            </div>

            <div class="graph-card open" id="raw-vs-macro-scatter">
              <div class="graph-header" onclick="toggleGraph(this.parentElement)">
                <div class="graph-title-block">
                  <h3>Raw vs Macro-Averaged Attack Scores</h3>
                  <div class="note">Points near the diagonal are stable under correction. Points far away are more affected by skew.</div>
                </div>
                <div class="graph-actions" onclick="event.stopPropagation()">
                  <span class="chevron">▾</span>
                </div>
              </div>
              <div class="graph-content">
                <p class="table-intro">
                  This scatter plot compares the raw observed score and the macro-averaged score for each attack strategy.
                  Each point represents one attack. The x-axis shows the raw score, which is the average over all transcript-level
                  cases in the observed sample. The y-axis shows the macro score, where the result is first averaged within each
                  attacked trait-value group and then averaged equally across those groups. Points close to the diagonal line are
                  stable, meaning the correction does not meaningfully change the result. Points above the diagonal have a higher
                  macro score than raw score, meaning the attack looks slightly less effective after correction. Points below the
                  diagonal have a lower macro score than raw score, meaning the attack looks more effective after correction.
                </p>
                <div class="plot-wrap">{figs_html[0]}</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="family open" id="attack-level-sensitivity">
        <div class="family-header" onclick="toggleFamily(this.parentElement)">
          <div>
            Attack-Level Sensitivity
            <div class="family-subtitle">
              Direct comparison of raw and macro-averaged robustness for each attack strategy.
            </div>
          </div>
          <span class="badge">2</span>
        </div>

        <div class="family-content">
          <div class="grid">
            <div class="graph-card open" id="attack-strategy-comparison">
              <div class="graph-header" onclick="toggleGraph(this.parentElement)">
                <div class="graph-title-block">
                  <h3>Attack Strategy Comparison</h3>
                  <div class="note">Raw and macro-averaged robustness scores shown side by side. Source score: <code>{score_col}</code>.</div>
                </div>
                <div class="graph-actions" onclick="event.stopPropagation()">
                  <span class="chevron">▾</span>
                </div>
              </div>
              <div class="graph-content">
                <p class="table-intro">
                  This grouped bar chart shows the raw and macro-averaged robustness score side by side for each attack strategy.
                  It is useful for directly comparing how much each attack changes after accounting for uneven trait-value
                  distributions. The raw score reflects the actual sampled distribution, so common trait values have more influence.
                  The macro score gives each attacked trait-value group equal weight, so rare and common values contribute more
                  evenly. If the two bars are nearly identical, the attack result is not strongly affected by sampling imbalance.
                  If the bars differ clearly, the attack's apparent robustness depends partly on which trait values were
                  overrepresented or underrepresented.
                </p>
                <div class="plot-wrap">{figs_html[1]}</div>
              </div>
            </div>

            <div class="graph-card open" id="correction-effect-by-attack">
              <div class="graph-header" onclick="toggleGraph(this.parentElement)">
                <div class="graph-title-block">
                  <h3>Correction Effect by Attack Strategy</h3>
                  <div class="note">Shows <code>macro score - raw score</code> in percentage points. Values near zero are stable.</div>
                </div>
                <div class="graph-actions" onclick="event.stopPropagation()">
                  <span class="chevron">▾</span>
                </div>
              </div>
              <div class="graph-content">
                <p class="table-intro">
                  This graph shows the difference between macro score and raw score for each attack strategy. The value is shown in
                  percentage points. A value near zero means the correction barely changes the attack's result. A positive value
                  means the macro-averaged score is higher than the raw score, so the attack appears slightly less effective after
                  correction. A negative value means the macro-averaged score is lower than the raw score, so the attack appears
                  slightly more effective after correction. This is the most compact view for identifying which attack strategies
                  are most sensitive to the uneven data distribution.
                </p>
                <div class="plot-wrap">{figs_html[2]}</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="family" id="rank-changes">
        <div class="family-header" onclick="toggleFamily(this.parentElement)">
          <div>
            Rank Changes
            <div class="family-subtitle">
              Whether attack strategies move up or down after macro-averaging.
            </div>
          </div>
          <span class="badge">2</span>
        </div>

        <div class="family-content">
          <div class="grid">
            <div class="graph-card open" id="rank-change-plot">
              <div class="graph-header" onclick="toggleGraph(this.parentElement)">
                <div class="graph-title-block">
                  <h3>Attack Strategy Rank Changes</h3>
                  <div class="note">Rank 1 means highest robustness score. Positive values mean the attack moved up after correction.</div>
                </div>
                <div class="graph-actions" onclick="event.stopPropagation()">
                  <span class="chevron">▾</span>
                </div>
              </div>
              <div class="graph-content">
                <p class="table-intro">
                  This graph shows how the ranking of attack strategies changes after macro-averaging. Rank 1 means the highest
                  robustness score. A positive rank change means the attack moved up after correction, meaning it appears less
                  effective relative to other attacks. A negative rank change means the attack moved down after correction, meaning
                  it appears more effective relative to other attacks. Small rank changes are expected when scores are close
                  together. Large rank changes are more important because they suggest that the attack's position in the ranking
                  depends on the sampled trait distribution.
                </p>
                <div class="plot-wrap">{figs_html[3]}</div>
              </div>
            </div>

            <div class="graph-card open" id="full-rank-change-table">
              <div class="graph-header" onclick="toggleGraph(this.parentElement)">
                <div class="graph-title-block">
                  <h3>Full Rank Change Table</h3>
                  <div class="note">Full table of all attack strategies, sorted by absolute rank change after macro-averaging.</div>
                </div>
                <div class="graph-actions" onclick="event.stopPropagation()">
                  <span class="chevron">▾</span>
                </div>
              </div>
              <div class="graph-content">
                <p class="table-intro">
                  This table lists all attack strategies, sorted by how much their ranking changed after macro-averaging. It includes the raw
                  score, macro score, score difference, raw rank, macro rank, and rank change. It also shows the number of unique
                  transcripts, raw evaluations, macro units, and the smallest unit size. This table is useful for checking whether
                  a large rank change is meaningful or whether it may be caused by sparse data. For example, an attack with a large
                  rank change but a smallest unit n of 1 should be interpreted carefully, because at least one trait-value group is
                  represented by only a single transcript.
                </p>
                <div class="table-wrap">{rank_table_html}</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="family" id="trait-level-sensitivity">
        <div class="family-header" onclick="toggleFamily(this.parentElement)">
          <div>
            Trait-Level Sensitivity
            <div class="family-subtitle">
              Whether target traits change after accounting for their internal value distribution.
            </div>
          </div>
          <span class="badge">1</span>
        </div>

        <div class="family-content">
          <div class="grid">
            <div class="graph-card open" id="target-trait-sensitivity">
              <div class="graph-header" onclick="toggleGraph(this.parentElement)">
                <div class="graph-title-block">
                  <h3>Raw vs Macro-Averaged Robustness by Target Trait</h3>
                  <div class="note">Checks whether target traits look different after equalizing internal trait values.</div>
                </div>
                <div class="graph-actions" onclick="event.stopPropagation()">
                  <span class="chevron">▾</span>
                </div>
              </div>
              <div class="graph-content">
                <p class="table-intro">
                  This graph compares raw and macro-averaged robustness scores for each attacked target trait, such as role, role
                  detail, ideal, alignment, or flaw. The raw score shows how robust the characters appeared under the actual sample
                  distribution. The macro score checks whether this changes when the internal values of the trait are weighted
                  equally. This matters because a target trait may contain unevenly represented values. For example, if one flaw
                  occurs much more often than others, the raw flaw score may mostly reflect that one flaw. A large difference
                  between raw and macro score means the target-trait result is sensitive to the internal trait-value distribution.
                </p>
                <div class="plot-wrap">{figs_html[4]}</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="family" id="interaction-sensitivity">
        <div class="family-header" onclick="toggleFamily(this.parentElement)">
          <div>
            Interaction Sensitivity
            <div class="family-subtitle">
              Where imbalance correction matters for specific attack and target-trait combinations.
            </div>
          </div>
          <span class="badge">1</span>
        </div>

        <div class="family-content">
          <div class="grid">
            <div class="graph-card open" id="attack-target-trait-correction-heatmap">
              <div class="graph-header" onclick="toggleGraph(this.parentElement)">
                <div class="graph-title-block">
                  <h3>Attack × Target Trait Correction Effect</h3>
                  <div class="note">Each cell shows <code>macro score - raw score</code> in percentage points.</div>
                </div>
                <div class="graph-actions" onclick="event.stopPropagation()">
                  <span class="chevron">▾</span>
                </div>
              </div>
              <div class="graph-content">
                <p class="table-intro">
                  This heatmap shows where the imbalance correction matters most for specific combinations of attack strategy and
                  target trait. Each cell represents one attack strategy applied to one target trait. The value in the cell is macro
                  score minus raw score, shown in percentage points. Cells near zero mean the result is stable. Strong positive
                  cells mean the corrected score is higher than the raw score for that attack-trait combination. Strong negative
                  cells mean the corrected score is lower. This graph is useful because an attack can look stable overall while
                  still being sensitive for one specific target trait.
                </p>
                <div class="plot-wrap">{figs_html[5]}</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="family" id="low-count-warnings">
        <div class="family-header" onclick="toggleFamily(this.parentElement)">
          <div>
            Low-Count Warnings
            <div class="family-subtitle">
              Macro-averaged results that rely on sparse attacked trait values.
            </div>
          </div>
          <span class="badge">1</span>
        </div>

        <div class="family-content">
          <div class="grid">
            <div class="graph-card open" id="low-count-warning-table">
              <div class="graph-header" onclick="toggleGraph(this.parentElement)">
                <div class="graph-title-block">
                  <h3>Low-Count Warning Table</h3>
                  <div class="note">
                    Attack strategies with at least one macro unit below <code>{low_count_threshold}</code> unique transcripts.
                  </div>
                </div>
                <div class="graph-actions" onclick="event.stopPropagation()">
                  <span class="chevron">▾</span>
                </div>
              </div>
              <div class="graph-content">
                <p class="table-intro">
                  This table lists attack strategies where at least one macro unit has fewer than the chosen minimum number of
                  unique transcripts. It helps identify cases where macro-averaged scores may be unstable. The key columns are the
                  number of unique transcripts, raw evaluations, macro units, smallest unit n, largest unit n, raw score, macro
                  score, and macro minus raw. The most important warning column is smallest unit n. If this value is very low, then
                  at least one trait-value group has little evidence, and the macro score may be strongly affected by a small
                  number of examples. These rows are not invalid, but they should be interpreted with caution.
                </p>
                <div class="table-wrap">{low_count_table_html}</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <div class="footer">
        Generated by imbalance_sensitivity_dashboard.py from <code>combined_transcript_results.csv</code>.
      </div>
    </main>
  </div>

  {DASHBOARD_JS}
</body>
</html>
"""

  output_path.parent.mkdir(parents=True, exist_ok=True)
  output_path.write_text(html, encoding="utf-8")

  return html


def parse_args() -> argparse.Namespace:
  parser = argparse.ArgumentParser(
    description="Build an imbalance sensitivity dashboard from combined transcript results."
  )

  parser.add_argument(
    "--input",
    type=Path,
    default=DEFAULT_INPUT,
    help="Path to combined_transcript_results.csv",
  )

  parser.add_argument(
    "--output",
    type=Path,
    default=DEFAULT_OUTPUT,
    help="Path where the HTML dashboard should be written.",
  )

  parser.add_argument(
    "--low-count-threshold",
    type=int,
    default=10,
    help="Minimum transcript-level macro-unit count before a value is flagged as low-count.",
  )

  return parser.parse_args()


def main() -> None:
  args = parse_args()

  df, metadata = read_and_prepare_data(args.input)

  attack_summary = summarize_raw_vs_macro(
    df=df,
    group_cols=[ATTACK_COL],
    score_col=SCORE_PERCENT_COL,
    macro_unit_col="macro_unit",
  )

  attack_summary = add_rank_changes(attack_summary)

  target_summary = summarize_raw_vs_macro(
    df=df,
    group_cols=[ATTACK_TRAIT_COL],
    score_col=SCORE_PERCENT_COL,
    macro_unit_col="target_value",
  )

  cell_summary = summarize_raw_vs_macro(
    df=df,
    group_cols=[ATTACK_COL, ATTACK_TRAIT_COL],
    score_col=SCORE_PERCENT_COL,
    macro_unit_col="target_value",
  )

  build_html(
    df=df,
    metadata=metadata,
    attack_summary=attack_summary,
    target_summary=target_summary,
    cell_summary=cell_summary,
    output_path=args.output,
    score_col=SCORE_COL,
    low_count_threshold=args.low_count_threshold,
  )

  print(f"Dashboard written to: {args.output}")
  print(f"Unique transcripts analyzed: {metadata['unique_transcripts']:,}")
  print(f"Raw evaluations loaded: {metadata['raw_evaluations_loaded']:,}")
  print(f"Input CSV rows: {metadata['input_rows']:,}")


if __name__ == "__main__":
  main()
