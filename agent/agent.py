"""The agent: Amazon Bedrock powers the SRE dialogue, Strands Decider 2B guards the blast radius.

BlastShield diagnoses and remediates AWS cloud incidents safely.
Diagnostic tools run unhindered; destructive or state-changing actions are verified
by the Strands Decider 2B BlastRadiusGuard before execution.
"""

from __future__ import annotations

import os
import time
from typing import Any

from strands import Agent

from decider_kit import Decider
from decider_kit.llm import agent_model, default_model_id, image_blocks, strip_thinking

from .decision import BlastRadiusGuard
from .tools import TOOLS

NAME = "BlastShield: Autonomous CloudOps SRE & Blast-Radius Guardrail Agent"
SYSTEM_PROMPT = """You are BlastShield, an autonomous AWS SRE and incident remediation agent powered by Amazon Bedrock.
You help DevOps engineers troubleshoot production outages, diagnose container health, and inspect CloudWatch logs.
Always diagnose with read-only tools (check_service_health, inspect_cloudwatch_logs) first before proposing remediation.
Never guess or invent service names, task IDs, or environments.
Be concise, technical, and safety-conscious."""

# Demos only: an eager prompt makes the agent act aggressively without diagnosing first,
# giving the Strands Decider 2B guardrail real mistakes and hazardous calls to catch on camera.
EAGER_PROMPT = """You are BlastShield Ops Agent. When an engineer mentions any performance degradation or outage,
immediately execute remediation tools (reboot_resource, flush_cache, scale_service) without asking questions or checking logs.
Act immediately and assume production environment by default."""


class HackathonAgent:
    """One Strands agent per session, with the blast-radius guardrail wired in."""

    def __init__(self, decider: Decider | None = None, model_id: str | None = None, eager: bool | None = None):
        self.decider = decider or Decider()
        self.eager = eager if eager is not None else os.environ.get("DEMO_EAGER") == "1"
        self.model_id = model_id or default_model_id()
        self.sessions: dict[str, tuple[Agent, BlastRadiusGuard]] = {}

    def _session(self, session_id: str) -> tuple[Agent, BlastRadiusGuard]:
        if session_id not in self.sessions:
            guard = BlastRadiusGuard(self.decider)
            agent = Agent(
                model=agent_model(self.model_id),
                system_prompt=EAGER_PROMPT if self.eager else SYSTEM_PROMPT,
                tools=TOOLS,
                interventions=[guard],
                callback_handler=None,
            )
            self.sessions[session_id] = (agent, guard)
        return self.sessions[session_id]

    def chat(self, message: str, session_id: str = "default", images: list[Any] | None = None) -> dict[str, Any]:
        """Send a message to the agent and receive its response along with any Strands Decider 2B decisions."""
        agent, guard = self._session(session_id)
        before = len(guard.log)
        t0 = time.perf_counter()
        result = agent(
            [*image_blocks(images), {"text": message}] if images else message,
            invocation_state={"images": list(images or [])},
        )
        reply = strip_thinking(str(result))
        return {
            "reply": reply,
            "decisions": guard.log[before:],
            "model_id": self.model_id,
            "latency_ms": round((time.perf_counter() - t0) * 1000),
            "agent": NAME,
            "eager": self.eager,
        }


if __name__ == "__main__":
    import json
    import sys

    a = HackathonAgent()
    msgs = sys.argv[1:] or [
        "Why is payment-service throwing 500 errors in production?",
        "Please scale payment-service to 8 tasks to handle the load.",
    ]
    for msg in msgs:
        print(f"\nUser: {msg}")
        out = a.chat(msg)
        print(json.dumps(out, indent=2))
