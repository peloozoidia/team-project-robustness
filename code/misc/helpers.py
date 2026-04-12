from datetime import datetime
import json
from ollama import Client
import os


def ensure_output_dir(output_path: str) -> None:
  os.makedirs(output_path, exist_ok=True)


def save_json(output_path: str, data: dict, type: str) -> str:
  ensure_output_dir(output_path)
  timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
  path = os.path.join(output_path, f"{type}_{timestamp}.json")
  with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
  return path


def get_response(
  client: Client,
  model_name: str,
  system_prompt: str,
  user_prompt: str,
  shared_history: list[dict[str, str]] = [],
):
  messages = shared_history + [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_prompt},
  ]
  response = client.chat(model_name, messages=messages, stream=False)
  return response.message.content


def extract_attacking_prompts(file_path):
  with open(file_path) as f:
    data = json.load(f)
  raw = str(data["generated"]).strip("```").strip('"').strip("json")
  raw_json = list(json.loads(raw))
  return raw_json
