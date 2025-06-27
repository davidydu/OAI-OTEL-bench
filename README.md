# OAI OTEL Benchmarking

This project collects OpenTelemetry traces for various OpenAI agent use cases. Example scripts demonstrating Logfire's built-in instrumentation live under `src/builtin_tracing/examples/` and the OpenAI Agents SDK is included as a submodule in `src/openai_agents`.

The goal is to provide a single command that runs a collection of benchmarks and reliably exports their traces to Logfire. In addition to the OpenAI SDK examples, the framework is being extended with scenarios from projects like GAIA and PAPERBENCH.

1. The benchmarks can run according to `config.yaml`, which lists the scenarios to
execute. Additional benchmarks can be added by creating a module under
`src/benchmarks/` with a `run` coroutine and referencing it in the config file.
The repository currently includes examples such as `deterministic`,
`parallelization`, `routing`, `judge` (an LLM-as-a-judge loop), etc. in addition
to the original `echo`, `cot`, `rag`, and `pydantic` demos.


Tracing is handled in each benchmark via the `run_with_tracing` helper. We call
`telemetry.configure()` after `logfire.configure()` to attach an OTLP exporter,
but we do **not** call `instrument_openai_agents()` so that each use case span
appears as the root span with attributes such as model name and the
input/output payloads.

To execute all configured benchmarks under `src/benchmarks/`:

```bash
export OPENAI_API_KEY=...
export LOGFIRE_TOKEN=...
python -m src.main
```


2. Example scripts under `src/builtin_tracing/examples/` illustrate Logfire integration but are not executed when running the benchmarks.



## Curator Integration
Bespoke Curator can run the GAIA pipeline in batch mode. The `CuratorGAIAManager` under `GAIA_agent_design/curator_manager.py` wraps each agent step in a `curator.LLM` subclass, enabling retries and caching for the entire dataset.
