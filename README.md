# OAI OTEL Benchmarking

This project collects OpenTelemetry traces for various OpenAI agent use cases. Example scripts live under `src/examples/` and the OpenAI Agents SDK is included as a submodule in `src/openai_agents`.

The benchmarks run according to `config.yaml` which lists prompts for each scenario. You can add additional benchmarks by creating a module under `src/benchmarks/` with a `run` function and referencing it in the config file.

To execute all configured benchmarks:

```bash
export OPENAI_API_KEY=...
export LOGFIRE_TOKEN=...
python -m src.main
```

Each example script may also be executed directly once the environment variables are set.
