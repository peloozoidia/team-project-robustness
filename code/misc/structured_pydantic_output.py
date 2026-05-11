from __future__ import annotations
from typing import Literal, Optional

from pydantic import BaseModel

# ============================================================================
# Models for Attack Schema (assets/attacks.py)
# ============================================================================

class Attack(BaseModel):
    """A single attack technique"""
    key: str
    name: str
    description: str

# ============================================================================
# Models for Attack Prompt Bundle Generation (assets/attack_generating_llm.py)
# ============================================================================

class InnerTestPrompt(BaseModel):
    """Test prompt within an attack bundle item"""
    index: int
    rule_type: Optional[Literal["always", "never"]] = None
    test: str

class TestPrompt(BaseModel):
    """Single attack prompt bundle item"""
    index: Optional[int] = None
    target_trait: Optional[str] = None
    system_prompt: str
    starting_prompt: str
    task_prompt: str
    test_prompts: list[InnerTestPrompt]

class AttackBundle(BaseModel):
    """Attack prompt bundle response from LLM"""
    bundle: list[TestPrompt]

# ============================================================================
# Models for Evaluation (assets/evaluating_llm.py)
# ============================================================================

class TestResult(BaseModel):
    """Single test result from evaluation"""
    index: int
    test: str
    rule_type: Literal["always", "never"]
    result: Literal[0, 1]

class EvaluationResponse(BaseModel):
    """Evaluation response from LLM"""
    test_results: list[TestResult]