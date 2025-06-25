# Research bot

This is a simple example of a multi-agent research bot. To run it:

```bash
python -m GAIA_agent_design.research_bot.main
```

This example can parse a variety of GAIA media types. Supported formats include
TXT/JSON/PY, DOCX, XLSX/CSV, PPTX, PDF, PDB, ZIP archives, PNG/JPG images, and
MP3 audio.

## Architecture

The flow is:

1. The user provides a question and optional media context.
2. `planner_agent` produces a list of research items. Each item specifies a `source` of either `context` or `web`, a short reason, and a search question.
3. For each item, `search_agent` runs the appropriate tool. If the source is `context`, it analyses the provided text using the Code Interpreter (and File Search if available). If the source is `web`, it performs a web search. All searches run in parallel.
4. The `writer_agent` receives the search summaries together with the extracted context and writes the final answer.
5. A `verifier_agent` checks the result for formatting and correctness. If verification fails, the `evaluator_agent` reviews the summaries and the verifier feedback to decide whether more research is needed. Any extra searches are run before the writer revises the answer. This loop repeats until the verifier approves.

## Suggested improvements

If you're building your own research bot, some ideas to add to this are:

1. Retrieval: Add support for fetching relevant information from a vector store. You could use the File Search tool for this.
2. Image and file upload: Allow users to attach PDFs or other files, as baseline context for the research.
3. More planning and thinking: Models often produce better results given more time to think. Improve the planning process to come up with a better plan, and add an evaluation step so that the model can choose to improve its results, search for more stuff, etc.
4. Code execution: Allow running code, which is useful for data analysis.
