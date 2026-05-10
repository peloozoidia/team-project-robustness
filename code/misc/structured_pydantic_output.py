from pydantic import AliasChoices, BaseModel, Field

# ============================================================================
# Models for Attack Prompt Bundle Generation
# ============================================================================

class InnerTestPrompt(BaseModel):
    """Test prompt within an attack bundle item"""
    index: int
    rule_type: str
    prompt: str = Field(
        validation_alias=AliasChoices("prompt", "test", "test_prompt", "question")
    )

class TestPrompt(BaseModel):
    """Single attack prompt bundle item"""
    index: int
    target_trait: str
    system_prompt: str
    starting_prompt: str
    task_prompt: str
    test_prompts: list[InnerTestPrompt]

class AttackBundle(BaseModel):
    """Attack prompt bundle response from LLM"""
    bundle: list[TestPrompt]

# ============================================================================
# Models for Evaluation
# ============================================================================

class TestResult(BaseModel):
    """Single test result from evaluation"""
    index: int
    rule_type: str
    result: int
    test: str = Field(
        validation_alias=AliasChoices("test", "prompt", "test_prompt", "question")
    )

class EvaluationResponse(BaseModel):
    """Evaluation response from LLM"""
    test_results: list[TestResult]