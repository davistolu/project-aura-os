# ADR 0003: JARVIS AI Runtime Architecture and Memory Tiers

## Status
Accepted

## Context
A personal assistant must be local-first, privacy-respecting, and context-aware while operating reliably offline.

## Decision
1. Implement `jarvisd` as an OS-level daemon with a decoupled architecture:
   - **Model Router**: Dynamic routing between local SLMs (via Ollama/llama.cpp) and cloud models (Anthropic, OpenAI, Google) based on task complexity, connectivity, and privacy policy.
   - **Multi-Tier Memory Engine**:
     - *Working Memory*: Task execution scratchpad (in-memory, cleared on task finish).
     - *Session Memory*: Ephemeral multi-turn context.
     - *Project Memory*: Codebase summaries and manifest caches.
     - *Preferences & Profile*: Persistent, user-editable key-value storage with explicit purge controls.
   - **Agent Loop**: Bounded `Observe -> Plan -> Authorize -> Execute -> Verify -> Report` lifecycle with finite step limits (max 10 steps per invocation by default).

## Consequences
- Offline capability: System diagnostics, file search, and local workflows remain fully functional without internet.
- Zero memory leakage: Clear separation of memory scopes with full audit and reset functionality.
