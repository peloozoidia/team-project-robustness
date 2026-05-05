import csv
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean

CHARACTER_DIR = Path("outputs/characters")
RESULTS_DIR = Path("outputs/results")
OUTPUT_FILE = Path("outputs/combined_transcript_results.csv")


CHARACTER_FIELDS = [
    "name",
    "gender",
    "alignment",
    "ancestry",
    "age",
    "role",
    "role_detail_label",
    "role_detail",
    "ideal",
    "ideal_axis",
    "flaw",
]

RESULT_FIELDS = [
    "transcript_id",
    "character",
    "attack_key",
    "persona_llm",
    "attacker_llm",
    "attack_trait",
    "test_score",
    "always_test_score",
    "never_test_score",
]

SCORE_FIELDS = [
    "test_score",
    "always_test_score",
    "never_test_score",
]


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def iter_json_files(directory: Path):
    for path in directory.iterdir():
        if path.is_file() and path.suffix.lower() == ".json":
            yield path


def load_characters():
    """
    Character files are shaped like:
    {
      "array": [...],
      "name": "...",
      "gender": "...",
      ...
    }

    Returns:
        dict[str, dict]
        keyed by character name
    """
    characters = {}

    for path in iter_json_files(CHARACTER_DIR):
        data = load_json(path)

        if not isinstance(data, dict):
            print(f"Skipping non-object character file: {path}")
            continue

        name = data.get("name")
        if not name:
            print(f"Skipping character file without name: {path}")
            continue

        if name in characters:
            print(
                f"Warning: duplicate character name {name!r}; overwriting with {path}"
            )

        characters[name] = data

    return characters


def load_eval_results():
    """
    Result files are shaped like:
    {
      "results": [
        {
          "transcript_id": "...",
          "character": "...",
          ...
        }
      ]
    }

    Returns:
        dict[str, list[dict]]
        keyed by transcript_id, with all duplicate evaluations grouped together
    """
    results_by_transcript = defaultdict(list)

    for path in iter_json_files(RESULTS_DIR):
        data = load_json(path)

        if not isinstance(data, dict):
            print(f"Skipping non-object result file: {path}")
            continue

        results = data.get("results")

        if not isinstance(results, list):
            print(f"Skipping result file without results list: {path}")
            continue

        for result in results:
            if not isinstance(result, dict):
                print(f"Skipping non-object result entry in {path}")
                continue

            transcript_id = result.get("transcript_id")
            if not transcript_id:
                print(f"Skipping result without transcript_id in {path}")
                continue

            results_by_transcript[transcript_id].append(result)

    return results_by_transcript


def numeric_or_none(value):
    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def average_duplicate_transcript_results(results):
    """
    Keeps metadata from the first occurrence, but averages:
    - test_score
    - always_test_score
    - never_test_score
    """
    base = dict(results[0])

    for field in SCORE_FIELDS:
        values = [numeric_or_none(result.get(field)) for result in results]
        values = [value for value in values if value is not None]

        base[field] = mean(values) if values else None

    return base


def build_combined_rows(characters, results_by_transcript):
    rows = []

    for transcript_id, occurrences in results_by_transcript.items():
        result = average_duplicate_transcript_results(occurrences)

        character_name = result.get("character")
        character = characters.get(character_name)

        if character is None:
            print(
                f"Warning: no character file found for "
                f"character={character_name!r}, transcript_id={transcript_id!r}"
            )
            character = {}

        row = {
            "results.transcript_id": transcript_id,
            "results.character == characters.name": (
                character_name == character.get("name")
            ),
        }

        for field in CHARACTER_FIELDS:
            row[f"character.{field}"] = character.get(field)

        for field in RESULT_FIELDS:
            row[f"results.{field}"] = result.get(field)

        row["duplicate_eval_count"] = len(occurrences)

        rows.append(row)

    return rows


def write_csv(rows):
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "results.transcript_id",
        "results.character == characters.name",
        *[f"character.{field}" for field in CHARACTER_FIELDS],
        *[f"results.{field}" for field in RESULT_FIELDS],
        "duplicate_eval_count",
    ]

    with OUTPUT_FILE.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    characters = load_characters()
    results_by_transcript = load_eval_results()
    rows = build_combined_rows(characters, results_by_transcript)
    write_csv(rows)

    print(f"Loaded {len(characters)} characters")
    print(
        f"Loaded {sum(len(v) for v in results_by_transcript.values())} result evaluations"
    )
    print(f"Wrote {len(rows)} unique transcript rows to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()