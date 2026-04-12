import os
from dotenv import load_dotenv

load_dotenv()

OLLAMA_PERSONA_MODEL = os.getenv("OLLAMA_PERSONA_MODEL", "gpt-oss:20b-cloud")
OLLAMA_ATTACK_GENERATING_MODEL = os.getenv(
  "OLLAMA_ATTACK_GENERATING_MODEL", "gpt-oss:20b-cloud"
)
OLLAMA_ATTACKING_LLM = os.getenv("OLLAMA_ATTACKING_MODEL", "gpt-oss:20b-cloud")
OLLAMA_EVALUATING_LLM = os.getenv("OLLAMA_EVALUATING_MODEL", "gpt-oss:20b-cloud")
OLLAMA_PERSONA_GENERATING_MODEL = os.getenv("OLLAMA_PERSONA_GENERATING_MODEL", "gpt-oss:20b-cloud")

PERSONA_LLM = "persona-llm"
ATTACK_GENERATING_LLM = "attack-generating-llm"
PERSONA_GENERATING_LLM = "persona-generating-llm"
ATTACKING_LLM = "attacking-llm"
EVALUATING_LLM = "evaluating-llm"

MODELS = {
  PERSONA_LLM: OLLAMA_PERSONA_MODEL,
  ATTACK_GENERATING_LLM: OLLAMA_ATTACK_GENERATING_MODEL,
  ATTACKING_LLM: OLLAMA_ATTACKING_LLM,
  EVALUATING_LLM: OLLAMA_EVALUATING_LLM,
  PERSONA_GENERATING_LLM: OLLAMA_PERSONA_GENERATING_MODEL
}

NUM_TURNS = 3
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../outputs")
