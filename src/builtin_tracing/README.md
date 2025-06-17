# Built-in tracing example

This directory shows how to run the OpenAI Agents SDK examples using Logfire's
built-in instrumentation.

The script `hello_world_with_logfire.py` runs the SDK's `basic/hello_world`
example while automatically exporting traces to Logfire.

To run the script:

```bash
export OPENAI_API_KEY=...
export LOGFIRE_TOKEN=...
python -m src.builtin_tracing.hello_world_with_logfire
```
