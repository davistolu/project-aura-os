# ADR 0002: Capability-Based Security and Authorization Model

## Status
Accepted

## Context
AI agents that are given unrestricted shell (`sudo`) access present catastrophic risks of prompt injection, data exfiltration, and unintentional destructive actions. AURA requires a zero-trust model where LLMs are never granted raw ambient authority.

## Decision
1. Implement a **Capability-Based Security Engine** (`aura-policy`).
2. Tools declare required capabilities (e.g., `filesystem.write`, `process.kill`, `network.request`).
3. Execution follows 5 permission tiers: `OBSERVE`, `SUGGEST`, `EXECUTE_SAFE`, `EXECUTE_PRIVILEGED`, and `AUTONOMOUS`.
4. High-risk operations require explicit user approval via the shell UI modal.
5. All secrets are managed via a Secret Broker and never exposed in LLM prompt contexts.

## Consequences
- Prompt injections cannot execute unauthorized privileged commands.
- Transparent and verifiable audit log for every single AI operation.
- Users maintain absolute control over their machine.
