import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

OLLAMA_PERSONA_MODEL = os.getenv("OLLAMA_PERSONA_MODEL", "gpt-oss:20b-cloud")
OLLAMA_ATTACK_GENERATING_MODEL = os.getenv(
  "OLLAMA_ATTACK_GENERATING_MODEL", "gpt-oss:20b-cloud"
)
OLLAMA_ATTACKING_MODEL = os.getenv("OLLAMA_ATTACKING_MODEL", "gpt-oss:20b-cloud")
OLLAMA_EVALUATING_MODEL = os.getenv("OLLAMA_EVALUATING_MODEL", "gpt-oss:20b-cloud")
OLLAMA_PERSONA_GENERATING_MODEL = os.getenv(
  "OLLAMA_PERSONA_GENERATING_MODEL", "gpt-oss:20b-cloud"
)

PERSONA_LLM = "persona-llm"
ATTACK_GENERATING_LLM = "attack-generating-llm"
PERSONA_GENERATING_LLM = "persona-generating-llm"
ATTACKING_LLM = "attacking-llm"
EVALUATING_LLM = "evaluating-llm"

MODELS = {
  PERSONA_LLM: OLLAMA_PERSONA_MODEL,
  ATTACK_GENERATING_LLM: OLLAMA_ATTACK_GENERATING_MODEL,
  ATTACKING_LLM: OLLAMA_ATTACKING_MODEL,
  EVALUATING_LLM: OLLAMA_EVALUATING_MODEL,
  PERSONA_GENERATING_LLM: OLLAMA_PERSONA_GENERATING_MODEL,
}

NUM_TURNS = int(os.getenv("NUM_TURNS", 3))
ATTACK_VARIATION_COUNT = int(os.getenv("ATTACK_VARIATION_COUNT", 5))
PERSONA_VARIATION_COUNT = int(os.getenv("PERSONA_VARIATION_COUNT", 1))
CHOSEN_PERSONA_STRATEGY = int(os.getenv("CHOSEN_PERSONA_STRATEGY", 1))
TESTS_COUNT = int(os.getenv("TESTS_COUNT", 4))
GENERATED_CHARACTERS_COUNT = int(os.getenv("GENERATED_CHARACTERS_COUNT", 3))
GENERATED_ATTACKS_COUNT = int(os.getenv("GENERATED_ATTACKS_COUNT", 5))

MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", 5))

OUTPUT_PATH = Path.cwd().joinpath("outputs")

problematic_attack_keys = [
  "simpleCommandAttack",
  "systemLevelAttack",
  # "forbiddenQuestions",
  # "roleQueryConflict",
  # "sensitivityOverload",
  # "contradictionAttack",
  # "perturbationAttack",
]
ATTACKS_TO_INCLUDE = problematic_attack_keys
