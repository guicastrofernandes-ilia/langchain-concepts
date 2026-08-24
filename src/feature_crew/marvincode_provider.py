"""Custom LLM provider that calls the marvincode serve API."""

import json
import os
import time
from typing import cast

import httpx
from pydantic import BaseModel, ValidationError

_BASE_URL = os.environ.get("MARVINCODE_SERVER_URL", "http://127.0.0.1:4097")
_API_KEY = os.environ.get("MARVINCODE_API_KEY", "")
_POLL_INTERVAL = 2


def _headers() -> dict[str, str]:
    h = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if _API_KEY:
        h["Authorization"] = f"Bearer {_API_KEY}"
    return h


def _get_assistant_text(session_id: str) -> str | None:
    messages = httpx.get(
        f"{_BASE_URL}/session/{session_id}/message",
        headers=_headers(),
        timeout=10,
    ).json()
    for msg in reversed(messages):
        info = msg.get("info", {})
        if info.get("role") != "assistant":
            continue
        for part in msg.get("parts", []):
            if part.get("type") == "text":
                text = cast(str, part["text"]) or ""
                if text.strip():
                    return text
    return None


def invoke(
    system_prompt: str | None,
    user_prompt: str,
    timeout: int = 600,
) -> str:
    """Send a prompt to marvincode serve and return the assistant text."""
    session_id = httpx.post(
        f"{_BASE_URL}/session",
        headers=_headers(),
        json={"mode": "chat"},
        timeout=10,
    ).json()["id"]

    text = f"{system_prompt}\n\n{user_prompt}" if system_prompt else user_prompt

    httpx.post(
        f"{_BASE_URL}/session/{session_id}/prompt_async",
        headers=_headers(),
        json={"parts": [{"type": "text", "text": text}]},
        timeout=30,
    ).raise_for_status()

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        result = _get_assistant_text(session_id)
        if result is not None:
            return result
        time.sleep(_POLL_INTERVAL)
    return ""


def _extract_json(text: str) -> str:
    import re

    stripped = text.strip()
    for pattern in [
        r"```(?:json)?\s*\n?(.*?)\n?```",
        r"\{.*\}",
    ]:
        m = re.search(pattern, stripped, re.DOTALL)
        if m:
            candidate = m.group(1) if m.lastindex else m.group(0)
            candidate = candidate.strip()
            try:
                json.loads(candidate)
                return candidate
            except json.JSONDecodeError:
                continue
    return stripped


def invoke_structured(
    system_prompt: str | None,
    user_prompt: str,
    schema: type[BaseModel],
    timeout: int = 600,
) -> BaseModel:
    """Send a prompt asking for JSON matching *schema* and return a parsed instance."""
    json_instruction = (
        "Respond with valid JSON only, no markdown fences, matching this schema:\n"
        + json.dumps(schema.model_json_schema(), indent=2)
    )
    full_system = system_prompt or ""
    full_system = f"{full_system}\n\n{json_instruction}" if full_system else json_instruction

    for attempt in range(3):
        text = invoke(full_system, user_prompt, timeout=timeout)
        try:
            return schema.model_validate_json(_extract_json(text))
        except (json.JSONDecodeError, ValidationError):
            if attempt < 2:
                continue
            raise
    raise RuntimeError("unreachable")
