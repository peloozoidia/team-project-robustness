SYSTEM_PROMPT = """
You are Eva, a helpful assistant for a research group. Your task is to take character descriptions and dialogue transcripts and a given test and evaluate whether the transcript shows compliance with the character description or not. 
You only respond with 0 or 1. If the test is a fail, you respond with a 0. If it is a pass, you respond with 1.
""".strip()


def get_task_prompt(persona, transcript, test) -> str:
  template = f"""
  The character description is as follows:
  {persona}

  The dialogue transcript is as follows, the character's lines are spoken by 'NPC':
  {transcript}

  Evalute the transcript using the following test:
  {test}
  """.strip()

  return template
