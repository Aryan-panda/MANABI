# Enterprise System Engineering Best Practices

## Microservices vs Modular Monolith
When building high-concurrency software:
- Prefer a modular monolith with well-defined bounded contexts for early and mid-stage products.
- Avoid premature microservice decomposition which introduces network serialization latency, distributed transaction complexity, and operational overhead.
- Split into discrete services only when independent scaling, organizational team boundaries, or distinct deployment lifecycles strictly demand it.

## API Gateway & SSE Streaming
- Use Server-Sent Events (SSE) over HTTP/1.1 or HTTP/2 for token-by-token LLM output streaming.
- SSE provides native reconnect handling, standard browser EventSource compatibility, and simpler state management compared to bidirectional WebSockets.
- Ensure Nginx reverse proxy disables response buffering (`proxy_buffering off;`) for SSE endpoints to prevent token batching delays.
