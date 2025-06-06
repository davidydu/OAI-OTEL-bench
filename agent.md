# AI Agent OTEL Benchmarking

## 1. Project Overview
Instrument OpenAI agent workflows (using openai-agents-python) with OpenTelemetry to capture spans and export traces to Logfire.

## 2. Use Cases
1. **Echo Demo:** Simple input → agent returns same text.
2. **Chain-of-Thought:** agentic reasoning over a multi-step prompt.
3. **Retrieval-Augmented Generation:** agent uses external knowledge.

## 3. Agent Framework
- **SDK:** openai-agents-python (see `src/openai_agents/`)
- **Entry point:** `Agent.run()`

## 4. Telemetry Plan
- **Tracer:** OpenTelemetry Python SDK
- **Exporter:** OTLP over HTTP → Logfire backend
- **Config:** via Pydantic models reading from `config.yaml`

## 5. Success Criteria
- One button click yields a JSON or database record of spans for any use case.
