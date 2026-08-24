"""Orchestrate the Planner, Coder, and Reviewer agents."""

from typing import cast

from feature_crew.agents import create_coder, create_planner, create_reviewer
from feature_crew.models import CodeArtifact, Plan, Review


class Crew:
    def __init__(self, model: str | None = None) -> None:
        self.model = model
        self.planner = create_planner(model)
        self.coder = create_coder(model)
        self.reviewer = create_reviewer(model)

    def run(self, description: str) -> tuple[Plan, CodeArtifact, Review]:
        plan = cast(Plan, self.planner.invoke({"description": description}))
        plan_text = f"{plan.summary}\n\nTasks:\n" + "\n".join(f"- {t}" for t in plan.tasks)
        code = cast(CodeArtifact, self.coder.invoke({"plan": plan_text}))
        review = cast(
            Review,
            self.reviewer.invoke(
                {
                    "plan": f"{plan.summary}\n\n" + "\n".join(plan.tasks),
                    "code": f"File: {code.filename}\n\n{code.code}",
                }
            ),
        )
        return plan, code, review
