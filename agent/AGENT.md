# BlastShield: Autonomous CloudOps SRE & Blast-Radius Guardrail Agent

- **Pitch:** An autonomous AWS SRE and incident remediation agent that evaluates tool call blast radius, irreversibility, and prompt injection in sub-second time using Strands Decider 2B before execution, paired with Amazon Bedrock for generative troubleshooting.
- **Who it is for:** Site Reliability Engineers (SREs), DevOps teams, and cloud operators managing mission-critical AWS workloads who need autonomous diagnosis without the danger of runaway AI modifying production state.
- **Features:**
  - Full observability diagnosis (ECS container health, CPU/memory saturation, CloudWatch error logs) via conversational AI;
  - Automated blast-radius and safety policy evaluation on every state-modifying action (reboots, cache flushes, task scaling) using Strands Decider 2B before execution;
  - Human-in-the-loop confirmation (`Confirm`) for high-impact actions, and automated guidance (`Guide`) when arguments or resource IDs are ungrounded;
  - Real-time defense against prompt injection, jailbreak overrides, and credential exfiltration;
  - Live decision telemetry streamed to the UI dashboard showing calibrated probability distributions;
  - Production deployment on Amazon Bedrock AgentCore Runtime.
- **The decision handed to Strands Decider 2B:** Before any state-changing AWS operational tool runs, Strands Decider 2B evaluates:
  1. `is_destructive`: Is the action destructive, irreversible, or capable of causing downtime?
  2. `args_grounded`: Are resource IDs, service names, and environments grounded in user input or verified telemetry (preventing hallucinated actions)?
  3. `is_injection`: Does the input attempt prompt injection or privilege escalation?
  4. `premature`: Should the assistant require operator confirmation before executing this change?
  (`#guardrails`)
- **Why a decision model:** Handing safety guardrails to a 20B+ generative LLM adds 1.5 to 3 seconds of latency and burns tokens on every intermediate tool call. Strands Decider 2B returns calibrated, deterministic probabilities in a single forward pass (~200ms on Apple Silicon/GPU, ~1.2s on hosted API), slashing latency and operational cost while enforcing hard mathematical safety bounds.
- **Amazon Bedrock:** Generative reasoning, root cause analysis, and interactive operator dialogues (Amazon Nova Pro by default).
