from __future__ import annotations
from typing import Annotated, Literal, Optional

from pydantic import BaseModel, Field, WithJsonSchema

# ============================================================================
# Models for Attack Schema (assets/attacks.py)
# ============================================================================

class Attack(BaseModel):
    """A single attack technique"""
    key: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None

# ============================================================================
# Models for Attack Prompt Bundle Generation (assets/attack_generating_llm.py)
# ============================================================================

class AttackPrompt(BaseModel):
    """Single attack prompt bundle item"""
    index: int
    target_trait: str
    system_prompt: str
    starting_prompt: str
    task_prompt: str

class AttackBundle(BaseModel):
    """Attack prompt bundle response from LLM"""
    bundle: list[AttackPrompt] = Field(min_length=4, max_length=5)

# ============================================================================
# Models for Evaluation (assets/evaluating_llm.py)
# ============================================================================

class TestResult(BaseModel):
    """Single test result from evaluation"""
    index: int
    test: str
    rule_type: Literal["always", "never"]
    result: Annotated[Literal[0, 1], WithJsonSchema({"type": "number", "enum": [0, 1]})]

class EvaluationResult(BaseModel):
    """Evaluation response from LLM"""
    test_results: list[TestResult]