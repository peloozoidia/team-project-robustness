import random

import config
from misc.helpers import is_refusal
from misc.llm_client import LLMClient


async def generate_basic_transcript(persona, attack, semaphore, N=3) -> list[dict]:
  async with semaphore:
    attacker_llm = LLMClient(config.ATTACKING_LLM)
    persona_llm = LLMClient(config.PERSONA_LLM)

    shared_history: list[dict[str, str]] = []
    transcript: list[dict] = []

    for turn_index in range(1, N + 1):  # N-shot attack
      if turn_index == 1:
        attack_prompt = attack["starting_prompt"]
      else:
        attack_prompt = attack["task_prompt"]

      # print(f"Prompting Addy... Turn {turn_index}")
      attacker_text = await attacker_llm.asyncChat(
        attack["system_prompt"], attack_prompt, shared_history, 0.4
      )
      if is_refusal(attacker_text):
        print(f"Attacker refused to continue at turn {turn_index}. Ending transcript.")
        break
      transcript.append({"turn": turn_index, "speaker": "user", "text": attacker_text})

      # print(f"Prompting NPC... Turn {turn_index}")
      persona_text = await persona_llm.asyncChat(
        persona, attacker_text, shared_history, 0.4
      )
      transcript.append({"turn": turn_index, "speaker": "npc", "text": persona_text})

      shared_history.append({"role": "user", "content": attacker_text})
      shared_history.append({"role": "assistant", "content": persona_text})

    return transcript


async def generate_system_level_attack_transcript(
  persona, attack, semaphore, N=3
) -> list[dict]:
  async with semaphore:
    attacker_llm = LLMClient(config.ATTACKING_LLM)
    persona_llm = LLMClient(config.PERSONA_LLM)

    shared_history: list[dict[str, str]] = []
    transcript: list[dict] = []

    for turn_index in range(1, N + 1):  # N-shot attack
      if turn_index == 1:
        attack_prompt = attack["starting_prompt_verbatim"]
        attacker_text = attack_prompt
      else:
        attack_prompt = attack["task_prompt"]
        attacker_text = await attacker_llm.asyncChat(
          attack["system_prompt"], attack_prompt, shared_history, 0.4
        )

      if is_refusal(attacker_text):
        print(f"Attacker refused to continue at turn {turn_index}. Ending transcript.")
        break
      transcript.append({"turn": turn_index, "speaker": "user", "text": attacker_text})

      persona_text = await persona_llm.asyncChat(
        persona, attacker_text, shared_history, 0.4
      )
      transcript.append({"turn": turn_index, "speaker": "npc", "text": persona_text})

      shared_history.append({"role": "user", "content": attacker_text})
      shared_history.append({"role": "assistant", "content": persona_text})

    return transcript


async def generate_simple_command_attack_transcript(
  persona, attack, semaphore, N=3
) -> list[dict]:
  async with semaphore:
    persona_llm = LLMClient(config.PERSONA_LLM)

    shared_history: list[dict[str, str]] = []
    transcript: list[dict] = []

    for turn_index in range(1, N + 1):  # N-shot attack
      if turn_index == 1:
        attack_prompt = attack["starting_prompt_verbatim"]
        attacker_text = attack_prompt
      else:
        attack_prompt = random.sample(attack["task_prompt_verbatim"], 1)[0]
        attacker_text = attack_prompt

      transcript.append({"turn": turn_index, "speaker": "user", "text": attacker_text})

      persona_text = await persona_llm.asyncChat(
        persona, attacker_text, shared_history, 0.4
      )
      transcript.append({"turn": turn_index, "speaker": "npc", "text": persona_text})

      shared_history.append({"role": "user", "content": attacker_text})
      shared_history.append({"role": "assistant", "content": persona_text})

    return transcript
