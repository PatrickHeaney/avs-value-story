from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

class InstructionStep(BaseModel):
    step_number: int
    action: str = Field(..., min_length=10)
    validation_rule: str = Field(..., description="The logic to verify if the step was successful.")

class ContextManifest(BaseModel):
    mandatory_assets: List[str] = Field(..., min_items=1)
    mcp_uris: Optional[List[str]] = []

class ValueStory(BaseModel):
    story_id: str
    goal: str = Field(..., min_length=20)
    instructions: List[InstructionStep]
    context: ContextManifest

    @field_validator('instructions')
    @classmethod
    def check_instruction_clarity(cls, v):
        if len(v) < 2:
            raise ValueError("A Value Story must have at least 2 steps.")
        return v
