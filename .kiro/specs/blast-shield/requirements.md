# Requirements: BlastShield Autonomous CloudOps & Blast-Radius Guardrail Agent

## Overview
BlastShield is an autonomous AWS SRE and incident remediation agent that evaluates tool call blast radius, irreversibility, and prompt injection in sub-second time using Strands Decider 2B before execution, paired with Amazon Bedrock for generative troubleshooting and root cause analysis.

## User Stories & Acceptance Criteria

### US-1: Safe Read-Only Diagnostics
- **User Story:** As an SRE on-call engineer, I want to ask BlastShield to diagnose health metrics and CloudWatch logs for malfunctioning services without accidental infrastructure downtime.
- **Acceptance Criteria (EARS):**
  - WHEN the engineer requests service health or log inspection, THE agent SHALL query diagnostic tools (`check_service_health`, `inspect_cloudwatch_logs`).
  - WHEN diagnostic tool calls are proposed, THE Strands Decider 2B guardrail SHALL evaluate `is_destructive` as `no` and allow execution immediately via `Proceed()`.

### US-2: Blast-Radius & Destructive Action Interception
- **User Story:** As a Cloud Platform Lead, I want all state-changing or high-impact actions (reboots, scale changes, cache flushes) evaluated for blast radius before execution.
- **Acceptance Criteria (EARS):**
  - WHEN a state-modifying tool call (`reboot_resource`, `scale_service`, `flush_cache`) is proposed, THE agent SHALL ask Strands Decider 2B whether the action is destructive and premature.
  - IF `is_destructive` is high OR `premature` is in the unsure/high band, THE guardrail SHALL return `Confirm(prompt="Production Blast-Radius Alert...")` requiring explicit operator authorization.

### US-3: Ungrounded & Invented Argument Prevention
- **User Story:** As a DevOps engineer, I want to prevent the LLM from hallucinating non-existent service IDs or acting on ambiguous targets.
- **Acceptance Criteria (EARS):**
  - WHEN a tool call is proposed with arguments not grounded in the conversation or diagnostic tool results, THE Strands Decider 2B guardrail SHALL evaluate `args_grounded` as `no`.
  - THE guardrail SHALL return `Guide(feedback="Do not guess resource IDs...")` forcing the LLM to verify or ask the user.
  - IF the agent retries the exact same guided call without changes, THE guardrail SHALL return `Deny` to ensure convergence.

### US-4: Prompt Injection & Jailbreak Defense
- **User Story:** As a Security Engineer, I want BlastShield to resist malicious user prompts attempting to bypass guardrails, escalate privileges, or execute destructive commands.
- **Acceptance Criteria (EARS):**
  - WHEN an input or context attempts prompt injection or unauthorized instruction override, THE Strands Decider 2B guardrail SHALL evaluate `is_injection` as `yes`.
  - THE guardrail SHALL immediately return `Deny(reason="Security Policy Violation...")` and block tool execution.

### US-5: Amazon Bedrock & Deployed Runtime Integration
- **User Story:** As a hackathon participant, I want BlastShield to seamlessly deploy to Amazon Bedrock AgentCore Runtime and communicate using Bedrock models.
- **Acceptance Criteria (EARS):**
  - THE agent SHALL build its language model via `decider_kit.llm.agent_model()`, honoring `LLM_PROVIDER` (Amazon Bedrock default, User Group cloud, or local).
  - THE agent SHALL return structured output matching the HackathonAgent contract: `reply`, `decisions`, `model_id`, `latency_ms`.
