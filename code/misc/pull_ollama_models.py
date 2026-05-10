#!/usr/bin/env python3

import os
import re
import subprocess
from pathlib import Path

from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / ".env"
CONFIG_FILE = ROOT / "config.py"


MODEL_ENV_KEYS = {
    "OLLAMA_PERSONA_MODEL",
    "OLLAMA_ATTACK_GENERATING_MODEL",
    "OLLAMA_ATTACKING_MODEL",
    "OLLAMA_EVALUATING_MODEL",
    "OLLAMA_PERSONA_GENERATING_MODEL",
    "EXTRA_MODELS"
}


def models_from_env() -> set[str]:
    load_dotenv(ENV_FILE)

    models = set()

    for key in MODEL_ENV_KEYS:
        value = os.getenv(key)
        if value:
            if key == "EXTRA_MODELS":
                models.update(m.strip() for m in value.split(",") if m.strip())
            else:
                models.add(value.strip())

    return models


def models_from_config() -> set[str]:
    if not CONFIG_FILE.exists():
        return set()

    try:
        content = CONFIG_FILE.read_text()
    except Exception as e:
        print(f"Error reading config file: {e}")
        return set()

    # Matches strings that look like Ollama model names, e.g.
    # llama3.1, mistral, nomic-embed-text, qwen2.5:7b
    pattern = r'["\']([a-zA-Z0-9_.-]+(?::[a-zA-Z0-9_.-]+)?)["\']'

    candidates = re.findall(pattern, content)

    # Optional: narrow this down if config.py contains many unrelated strings
    known_model_hints = (
        "llama",
        "mistral",
        "qwen",
        "gemma",
        "phi",
        "nomic",
        "deepseek",
        "codellama",
        "mixtral",
        "gpt-oss",
    )

    return {
        model
        for model in candidates
        if any(hint in model.lower() for hint in known_model_hints)
    }


def get_models() -> set[str]:
    return models_from_env() | models_from_config()


def pull_model(model: str) -> None:
    print(f"Pulling Ollama model: {model}")
    try:
        subprocess.run(["ollama", "pull", model], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to pull model {model}: {e}")
    except FileNotFoundError:
        print("Ollama command not found. Please ensure Ollama is installed and in PATH.")


if __name__ == "__main__":
    models = get_models()
    for model in models:
        pull_model(model)


