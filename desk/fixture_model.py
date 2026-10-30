"""An Agno Model that needs no API key: it implements the six abstract methods of agno.models.base.Model.

Agno calls invoke(messages=..., tools=..., response_format=...) and expects a ModelResponse back. A real provider sends the
messages to an API; this one reads the agent's role marker from the system message and answers deterministically:

  ROLE: triage   -> JSON matching the Triage output_schema (fixture_logic.plan)
  ROLE: compose  -> a cited answer from the evidence pack (fixture_logic.compose)
  ROLE: raise    -> a tool call to the confirmable ticket tool, then a one-line confirmation once the tool has run
  ROLE: article  -> a draft knowledge article from a gap cluster (fixture_logic.article)
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, AsyncIterator, Iterator

from agno.models.base import Model
from agno.models.response import ModelResponse

from desk import fixture_logic


def _text(m) -> str:
    c = m.content
    return c if isinstance(c, str) else json.dumps(c) if c is not None else ""


@dataclass
class FixtureModel(Model):
    id: str = "fixture-v1"
    name: str = "FixtureModel"
    provider: str = "fixture"

    def _respond(self, messages=None, tools=None, response_format=None, **_) -> ModelResponse:
        messages = messages or []
        system = next((_text(m) for m in messages if m.role == "system"), "")
        user = next((_text(m) for m in reversed(messages) if m.role == "user"), "")
        tool_results = [m for m in messages if m.role == "tool"]
        if "ROLE: triage" in system:
            ctx = json.loads(user)
            return ModelResponse(role="assistant", content=json.dumps(fixture_logic.plan(ctx["message"], ctx.get("role", ""))))
        if "ROLE: compose" in system:
            return ModelResponse(role="assistant", content=fixture_logic.compose(json.loads(user)))
        if "ROLE: article" in system:
            return ModelResponse(role="assistant", content=fixture_logic.article(json.loads(user)))
        if "ROLE: raise" in system:
            if tool_results:
                return ModelResponse(role="assistant", content=f"Submitted. {_text(tool_results[-1])}")
            proposal = json.loads(user)
            name = proposal.pop("tool")
            return ModelResponse(role="assistant", content=None, tool_calls=[{
                "id": "call_raise_1", "type": "function", "function": {"name": name, "arguments": json.dumps(proposal)}}])
        return ModelResponse(role="assistant", content="(fixture model: no role marker)")

    def invoke(self, *args, **kwargs) -> ModelResponse:
        return self._respond(**kwargs)

    async def ainvoke(self, *args, **kwargs) -> ModelResponse:
        return self._respond(**kwargs)

    def invoke_stream(self, *args, **kwargs) -> Iterator[ModelResponse]:
        yield self._respond(**kwargs)

    async def ainvoke_stream(self, *args, **kwargs) -> AsyncIterator[ModelResponse]:
        yield self._respond(**kwargs)

    def _parse_provider_response(self, response: Any, **kwargs) -> ModelResponse:
        return response

    def _parse_provider_response_delta(self, response: Any) -> ModelResponse:
        return response
