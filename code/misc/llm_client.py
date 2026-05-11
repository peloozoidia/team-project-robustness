import config
from ollama import AsyncClient, Client
from pydantic import BaseModel
from typing import Type


class LLMClient:
  def __init__(self, role: str) -> None:
    self.model = config.MODELS[role]
    self.client = Client()
    self.async_client = AsyncClient()

  def chat(
    self,
    system_prompt: str,
    user_prompt: str,
    shared_history: list[dict] = [],
    temperature: float = 0.4,
    format: Type[BaseModel] | None = None,
  ):
    messages = shared_history + [
      {"role": "system", "content": system_prompt},
      {"role": "user", "content": user_prompt},
    ]

    options = {
      "temperature": temperature,
    }

    try:
      response = self.client.chat(
        self.model, messages, options=options, stream=False,
        format=format.model_json_schema() if format else None,
      )
      message = response.message.content
      if message:
        return message.strip()
      else:
        raise Exception("Message returned was None")
    except Exception as exc:  # pragma: no cover - best-effort fallback path
      raise RuntimeError(f"LLM call failed using model '{self.model}': {exc}") from exc

  async def asyncChat(
    self,
    system_prompt: str,
    user_prompt: str,
    shared_history: list[dict] = [],
    temperature: float = 0.4,
    format: Type[BaseModel] | None = None,
  ):
    messages = shared_history + [
      {"role": "system", "content": system_prompt},
      {"role": "user", "content": user_prompt},
    ]

    options = {
      "temperature": temperature,
    }

    try:
      response = await self.async_client.chat(
        self.model, messages, options=options, stream=False,
        format=format.model_json_schema() if format else None,
      )
      message = response.message.content
      if message:
        return message.strip()
      else:
        raise Exception("Message returned was None")
    except Exception as exc:  # pragma: no cover - best-effort fallback path
      raise RuntimeError(f"LLM call failed using model '{self.model}': {exc}") from exc
