"""LangChain agent definitions for the feature crew (backed by marvincode serve)."""

from typing import Any, cast

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableLambda

from feature_crew.marvincode_provider import invoke_structured
from feature_crew.models import CodeArtifact, Plan, Review

PLANNER_SYSTEM = (
    "You are a senior product engineer. Given a feature description, "
    "produce a concise implementation plan with an ordered task list. "
    "Each task should be actionable and small enough for one code change.\n\n"
    "RESPOND WITH VALID JSON ONLY. No explanations, no markdown, no extra text. "
    "Your entire response must be parseable as the requested JSON schema."
)

CODER_SYSTEM = (
    "You are a pragmatic software engineer. Given a feature plan, "
    "produce a single, self-contained source file that implements the feature. "
    "Prefer Python. Include brief docstrings and type hints where helpful.\n\n"
    "RESPOND WITH VALID JSON ONLY. No explanations, no markdown, no extra text. "
    "Your entire response must be parseable as the requested JSON schema."
)

REVIEWER_SYSTEM = (
    "You are a strict code reviewer. Given a feature plan and a code artifact, "
    "decide whether the code satisfies the plan. Be concrete and actionable. "
    "Only pass if the code is complete, correct, and follows the plan.\n\n"
    "RESPOND WITH VALID JSON ONLY. No explanations, no markdown, no extra text. "
    "Your entire response must be parseable as the requested JSON schema."
)


def create_planner(
    model: str | None = None,
    api_key: str | None = None,
) -> Runnable[dict[str, Any], Plan]:
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", PLANNER_SYSTEM),
            ("human", "Feature description:\n{description}"),
        ]
    )

    def invoke_impl(inputs: dict[str, Any]) -> Plan:
        user_msg = prompt.format(**inputs)
        return cast(Plan, invoke_structured(PLANNER_SYSTEM, user_msg, Plan))

    return cast(Runnable[dict[str, Any], Plan], RunnableLambda(invoke_impl))


def create_coder(
    model: str | None = None,
    api_key: str | None = None,
) -> Runnable[dict[str, Any], CodeArtifact]:
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", CODER_SYSTEM),
            (
                "human",
                "Feature plan:\n{plan}\n\n"
                "Implement the feature. Return the filename and full code.",
            ),
        ]
    )

    def invoke_impl(inputs: dict[str, Any]) -> CodeArtifact:
        user_msg = prompt.format(**inputs)
        return cast(CodeArtifact, invoke_structured(CODER_SYSTEM, user_msg, CodeArtifact))

    return cast(Runnable[dict[str, Any], CodeArtifact], RunnableLambda(invoke_impl))


def create_reviewer(
    model: str | None = None,
    api_key: str | None = None,
) -> Runnable[dict[str, Any], Review]:
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", REVIEWER_SYSTEM),
            ("human", "Plan:\n{plan}\n\nCode artifact:\n{code}\n\nProvide a review."),
        ]
    )

    def invoke_impl(inputs: dict[str, Any]) -> Review:
        user_msg = prompt.format(**inputs)
        return cast(Review, invoke_structured(REVIEWER_SYSTEM, user_msg, Review))

    return cast(Runnable[dict[str, Any], Review], RunnableLambda(invoke_impl))
