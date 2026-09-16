# ADR-003: Model Gateway Pattern for Multi-Provider LLM Decoupling

## Status
Accepted

## Context
Agents in MANABI need to communicate with state-of-the-art LLMs. Directly importing vendor SDKs (such as google-generativeai or openai) into agent classes tightly couples domain reasoning to vendor-specific APIs, error formats, and pricing schemes. Furthermore, developers frequently want to run local models via Ollama to avoid API charges or privacy concerns during testing.

## Decision
Implement an internal **Model Gateway** with a unified `LLMProvider` interface:
- Supported providers: `GeminiProvider`, `OpenAIProvider`, and `OllamaProvider`.
- Ollama is treated as an external HTTP endpoint and is explicitly not containerized or downloaded automatically.
- The Gateway handles:
  1. Provider and model routing based on runtime configuration (`LLM_PROVIDER`, `LLM_MODEL`).
  2. Bounded retries with exponential backoff and jitter.
  3. Latency measurement and token usage tracking.
  4. Unified Server-Sent Events (SSE) streaming generator.
  5. Fallback mechanisms if primary provider fails or exceeds rate limits.

## Alternatives Considered
1. **Direct SDK usage within agents**:
   - *Rejected*: Vendor lock-in, duplicate retry/logging code across agents, inability to switch to local Ollama seamlessly.
2. **Third-party SaaS LLM gateways (Portkey / LiteLLM proxy container)**:
   - *Rejected*: Adds another infrastructure hop and external dependency. An internal Python abstraction provides full control with zero overhead.

## Consequences
- **Positive**: Clean separation of agent reasoning from provider mechanics; zero code changes needed in agents when switching providers or running offline with Ollama.
- **Negative**: Internal gateway must normalize streaming chunks and error types across different provider protocols.
