#!/usr/bin/env python3

import os
from pathlib import Path

import ollama
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / "code/.env"


MODEL_ENV_KEYS = {
  "OLLAMA_PERSONA_MODEL",
  "OLLAMA_ATTACK_GENERATING_MODEL",
  "OLLAMA_ATTACKING_MODEL",
  "OLLAMA_EVALUATING_MODEL",
  "OLLAMA_PERSONA_GENERATING_MODEL",
}


def models_from_env() -> set[str]:
  load_dotenv(ENV_FILE)

  models = set()

  for key in MODEL_ENV_KEYS:
    value = os.getenv(key)
    if value:
      models.add(value.strip())

  return models


def get_models() -> set[str]:
  return models_from_env()


def pull_model(model: str) -> None:
  print(f"Pulling Ollama model: {model}")
  try:
    ollama.pull(model)
  except Exception as e:
    print(f"Failed to pull model {model}: {e}")


if __name__ == "__main__":
  models = get_models()
  for model in models:
    pull_model(model)
