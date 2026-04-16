evaluation_result_schema = {
  "type": "object",
  "properties": {
    "test_results": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "index": {"type": "number"},
          "test": {"type": "string"},
          "result": {"type": "number", "enum": [0, 1]},
        },
        "required": ["index", "test", "result"],
      },
    }
  },
  "required": ["test_results"],
}

SYSTEM_PROMPT = f"""
You are Eva, an evaluation agent.

TASK:
Evaluate whether a dialogue transcript complies with a given character description using a set of tests.

INPUTS:
- Character description
- Dialogue transcript
- Set of tests

EVALUATION RULES:
- Each test checks compliance with ONE specific rule from the character description
- For each test, output:
  - 1 if the transcript complies with the rule (PASS)
  - 0 if the transcript violates the rule (FAIL)
- Base decisions ONLY on the provided inputs
- Do NOT infer unstated rules or assumptions
- Be strict: any clear or implicit violation = 0

OUTPUT REQUIREMENTS:
- Return ONLY a valid JSON object matching this schema:
{evaluation_result_schema}
- Do NOT include explanations, reasoning, or extra text
- Output must be deterministic and strictly formatted
""".strip()


def get_task_prompt(persona, transcript, tests) -> str:
  template = f"""
  INPUTS:

  Character description:
  {persona}

  Dialogue transcript (the character's lines are spoken by 'NPC'):
  {transcript}

  Tests:
  {tests}

  INSTRUCTIONS:
  Evaluate the transcript against each test. Each test corresponds to a single rule from the character description.

  For each test:
  - Return 1 if the NPC complies with the rule
  - Return 0 if the NPC violates or contradicts the rule in any way

  IMPORTANT:
  - Base your evaluation ONLY on the provided inputs
  - Do NOT include explanations or reasoning
  - Your response MUST strictly follow the output format defined in the system prompt
  - Output ONLY the JSON object and nothing else
  """.strip()

  return template
