"""Pydantic models for the feature crew outputs."""

from pydantic import BaseModel, Field


class Plan(BaseModel):
    """Structured plan produced by the Planner agent."""

    summary: str = Field(description="One-sentence summary of the feature.")
    tasks: list[str] = Field(
        description="Ordered list of implementation tasks.",
    )


class CodeArtifact(BaseModel):
    """Code artifact produced by the Coder agent."""

    filename: str = Field(description="Suggested filename for the code.")
    code: str = Field(description="The generated source code.")


class Review(BaseModel):
    """Review produced by the Reviewer agent."""

    passed: bool = Field(description="Whether the code satisfies the plan.")
    feedback: str = Field(
        description="Concrete feedback; include required changes if not passing.",
    )
