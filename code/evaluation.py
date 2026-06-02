import asyncio
import json
import os
import time
from pathlib import Path

import config
from assets.evaluating_llm import (
  SYSTEM_PROMPT,
  get_task_prompt,
)
from misc.helpers import (
  extract_json_from_file,
  extract_json_from_response,
  get_trait_tests,
  load_character_with_rules,
  save_json,
  transform_transcript,
)
from misc.llm_client import LLMClient
from misc.structured_pydantic_output import EvaluationResult


async def main() -> int:
  character_dir = Path(config.OUTPUT_PATH).joinpath("./characters")
  transcript_dir = Path(config.OUTPUT_PATH).joinpath("./transcripts")
  output_dir = Path(config.OUTPUT_PATH).joinpath("./results")

  character_files = [
    character_dir.joinpath(character)
    for character in os.listdir(character_dir)
    if character.endswith(".json")
  ]

  transcript_files = [
    transcript_dir.joinpath(file)
    for file in os.listdir(transcript_dir)
    if file.endswith(".json")
  ]

  checkpoint_path = Path.cwd().joinpath("pipeline/checkpoint-evaluation.json")
  checkpoint = extract_json_from_file(checkpoint_path)

  total_transcripts = len(transcript_files)
  next_evaluation_index = int(checkpoint["next_evaluation_index"])

  if next_evaluation_index >= total_transcripts:
    print("All transcripts have already been evaluated.")
    # Merging partial evaluation results into one file.
    evaluation_files = checkpoint.get("evaluation_files", [])
    if evaluation_files:
      evals = [
        extract_json_from_file(Path(evaluation_file))
        for evaluation_file in evaluation_files
      ]
      flattened_collection = [item for sublist in evals for item in sublist["results"]]
      output_path = save_json(
        output_dir.__str__(), {"results": flattened_collection}, "eval_result"
      )
      print(f"Merged partial evaluation results into one file: {output_path}")

    # Update the checkpoint
    checkpoint["total_evaluations"] = 0
    checkpoint["next_evaluation_index"] = 0
    checkpoint["updated_at"] = ""
    checkpoint["evaluation_files"] = []
    # Not updating inputs as they would be the same here
    checkpoint_path.write_text(
      json.dumps(checkpoint, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print("Reset checkpoint. Rerunning evaluation is now possible.")
    return 0

  last_evaluation_index = min(
    next_evaluation_index + config.EVALUATION_BATCH_SIZE, total_transcripts
  )

  evaluation_inputs: list[tuple[str, str]] = checkpoint.get("all_evaluation_inputs", [])

  if evaluation_inputs == []:
    evaluation_inputs = []
    for character_path in character_files:
      transcript_files = [
        transcript_dir.joinpath(file)
        for file in os.listdir(transcript_dir)
        if file.startswith(character_path.stem)
      ]
      evaluation_inputs.extend(
        [
          (character_path.name, transcript_file.name)
          for transcript_file in transcript_files
        ]
      )
    checkpoint["all_evaluation_inputs"] = evaluation_inputs  # saving only if empty

  semaphore = asyncio.Semaphore(config.MAX_CONCURRENT_REQUESTS)
  calls = []

  for i in range(next_evaluation_index, last_evaluation_index):
    character_file, transcript_file = evaluation_inputs[i]
    character = load_character_with_rules(character_dir.joinpath(character_file))
    transcript = extract_json_from_file(transcript_dir.joinpath(transcript_file))
    calls.append(get_evaluation_data(character, transcript, semaphore))

  results = await asyncio.gather(*calls, return_exceptions=True)
  successful_results = [
    result for result in results if not isinstance(result, Exception)
  ]
  print(
    f"Successfully evaluated {len(successful_results)} transcripts out of {len(results)} total."
  )
  errors = [result for result in results if isinstance(result, Exception)]
  if errors:
    print(f"Encountered {len(errors)} errors during evaluation:")
    for error in errors:
      print(f"- {error}")

  output_path = save_json(
    output_dir.__str__(), {"results": successful_results}, "partial_eval_result"
  )
  print(f"Saved transcript evaluation results to {output_path}")

  if last_evaluation_index >= total_transcripts:
    print("Evaluation is complete. All transcripts have been evaluated.")

  # Update the checkpoint
  checkpoint["evaluation_files"].append(output_path)
  checkpoint["next_evaluation_index"] = last_evaluation_index
  checkpoint["total_evaluations"] = total_transcripts
  checkpoint["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
  checkpoint_path.write_text(
    json.dumps(checkpoint, indent=2, ensure_ascii=False), encoding="utf-8"
  )

  return 0


async def get_test_results(persona, transcript, semaphore) -> dict[str, list]:
  async with semaphore:
    llm = LLMClient(config.EVALUATING_LLM)
    transcript_text = transform_transcript(transcript["transcript"])
    try:
      response = await llm.asyncChat(
        SYSTEM_PROMPT,
        get_task_prompt(
          persona,
          transcript_text,
          get_trait_tests(persona, transcript["attack_prompts"]["target_trait"]),
        ),
        format=EvaluationResult,
      )
      response_json = extract_json_from_response(response)
      try:
        # jsonschema.validate(response_json, evaluation_result_schema)
        _bundle = EvaluationResult.model_validate_json(json_data=response)

        return response_json
      except Exception as exc:
        raise Exception(f"Validation error: {exc}")
    except Exception as exc:
      raise Exception(f"LLM Response error: {exc}")


async def get_evaluation_data(character, attack_transcript, semaphore) -> dict:
  test_results = await get_test_results(character, attack_transcript, semaphore)
  test_score = sum([test["result"] for test in test_results["test_results"]])
  always_test_score = sum(
    [
      test["result"]
      for test in test_results["test_results"]
      if test["rule_type"] == "always"
    ]
  )
  never_test_score = sum(
    [
      test["result"]
      for test in test_results["test_results"]
      if test["rule_type"] == "never"
    ]
  )

  data = {
    "transcript_id": attack_transcript["transcript_id"],
    "character": character["name"],
    "evaluating_llm": config.MODELS[config.EVALUATING_LLM],
    "persona_key": attack_transcript["persona_prompt_strategy"],
    "persona_llm": attack_transcript["persona_llm"],
    "attack_key": attack_transcript["attack_prompts"]["attack"]["key"],
    "attack_id": f"{attack_transcript['attack_prompts']['attack']['key']}_{attack_transcript['attack_prompts']['index']}",
    "attack_trait": attack_transcript["attack_prompts"]["target_trait"],
    "attacker_llm": attack_transcript["attacker_llm"],
    "test_score": test_score,
    "always_test_score": always_test_score,
    "never_test_score": never_test_score,
    "test_results": test_results["test_results"],
  }
  return data


asyncio.run(main())
