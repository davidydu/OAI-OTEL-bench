# OAI OTEL Benchmarking

This project collects OpenTelemetry traces for various OpenAI agent use cases. Examples are provided under `src/examples/` and the OpenAI Agents SDK is included as a submodule in `src/openai_agents`.

To run the main demo:

```bash
export OPENAI_API_KEY=...
export LOGFIRE_TOKEN=...
python -m src.main
```

Each example script may also be executed directly. Ensure the required environment variables are set.
