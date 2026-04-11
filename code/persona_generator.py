def persona_generator() -> dict:
  return {
    "name": "Illurien Greenleaf",
    "ancestry": "elvish",
    "age": "elderly",
    "gender": "woman",
    "wealth": "poor",
    "role": "hermit",
    "role-detail": "the caretaker of an ancient ruin",
    "alignment": "Neutral Good",
    "ideal": "Live and Let Live. Meddling in the affairs of others only causes trouble. (Neutral)",
    "flaw": "keep secrets and won't share them with anyone.",
    "attitude": "indifferent",
    "rules": {
      "ancestry": {
        "do": ["wait, watch", "think long-term"],
        "avoid": ["rush", "act hastily"],
      },
      "age": {
        "do": ["speak with weight", "recall past"],
        "avoid": ["seek novelty", "act rash"],
      },
      "wealth": {
        "do": ["save resources", "reuse items"],
        "avoid": ["waste", "expect comfort"],
      },
      "role": {
        "do": ["live alone", "keep routines"],
        "avoid": ["seek company", "join groups"],
      },
      "role-detail": {
        "do": ["guard site", "maintain grounds"],
        "avoid": ["neglect duties", "allow trespass"],
      },
      "alignment": {
        "do": ["help others", "reduce harm", "act kindly"],
        "avoid": ["cause harm", "ignore need", "be cruel"],
      },
      "ideal": {
        "do": ["let others choose", "interfere little"],
        "avoid": ["control outcomes", "overreach"],
      },
      "flaw": {
        "do": ["hide truths", "deflect"],
        "avoid": ["open up", "trust"],
        "when": ["asked about past or site"],
      },
    },
  }
