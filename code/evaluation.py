import asyncio
import os
from pathlib import Path

import config
import jsonschema
from assets.evaluating_llm import (
  SYSTEM_PROMPT,
  evaluation_result_schema,
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

  semaphore = asyncio.Semaphore(config.MAX_CONCURRENT_REQUESTS)
  calls = []

  for character_path in character_files:
    character = load_character_with_rules(character_path)

    transcript_files = [
      transcript_dir.joinpath(file)
      for file in os.listdir(transcript_dir)
      if file.startswith(character_path.stem)
    ]
    transcripts = [extract_json_from_file(file) for file in transcript_files]

    generations = [
      get_evaluation_data(character, attack_transcript, semaphore)
      for attack_transcript in transcripts
    ]
    calls.extend(generations)

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
    output_dir.__str__(), {"results": successful_results}, "eval_result"
  )
  print(f"Saved transcript evaluation results to {output_path}")
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
        bundle = EvaluationResult.model_validate_json(json_data=response)      

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
