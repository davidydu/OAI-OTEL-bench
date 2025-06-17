# OAI OTEL Benchmarking

This project collects OpenTelemetry traces for various OpenAI agent use cases. Example scripts live under `src/examples/` and the OpenAI Agents SDK is included as a submodule in `src/openai_agents`.


The benchmarks run according to `config.yaml`, which lists the scenarios to
execute. Additional benchmarks can be added by creating a module under
`src/benchmarks/` with a `run` coroutine and referencing it in the config file.
The repository currently includes examples such as `deterministic`,
`parallelization`, `routing`, and `judge` (an LLM-as-a-judge loop) in addition
to the original `echo`, `cot`, `rag`, and `pydantic` demos.


Tracing is handled in each benchmark via the `run_with_tracing` helper. We call
`telemetry.configure()` after `logfire.configure()` to attach an OTLP exporter,
but we do **not** call `instrument_openai_agents()` so that each use case span
appears as the root span with attributes such as model name and the
input/output payloads.


Example scripts under `src/examples/` illustrate Logfire integration but are not
executed when running the benchmarks.

To execute all configured benchmarks:

```bash
export OPENAI_API_KEY=...
export LOGFIRE_TOKEN=...
python -m src.main
```

Each example script may also be executed directly once the environment variables are set.

