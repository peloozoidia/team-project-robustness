import config
from misc.llm_client import LLMClient


def main() -> None:
  llm = LLMClient(config.EVALUATING_LLM)
  try:
    response = llm.chat(
      "You are a helpful assistant and only respond with simple, utf-8 codable characters.",
      "Say hi to me using only simple characters. Don't use any emojis or special characters that the charmap codec maps to undefined.",
    )
    print(response)
  except Exception as exc:
    print(f"LLM access test failed: {exc}")
