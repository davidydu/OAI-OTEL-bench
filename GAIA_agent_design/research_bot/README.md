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
4. `evaluator_agent` reviews the initial search results **once** and may request one additional round of research.
5. Any extra searches are executed in parallel and the combined summaries are passed to `writer_agent`.
6. `writer_agent` composes the reasoning trace and final answer.
7. `verifier_agent` judges the answer. If formatting is off, the writer corrects it; if the reasoning appears wrong, the evaluator decides whether more research is necessary before rewriting.

## Suggested improvements

If you're building your own research bot, some ideas to add to this are:

1. Retrieval: Add support for fetching relevant information from a vector store. You could use the File Search tool for this.
2. Image and file upload: Allow users to attach PDFs or other files, as baseline context for the research.
3. More planning and thinking: Models often produce better results given more time to think. Improve the planning process to come up with a better plan, and add an evaluation step so that the model can choose to improve its results, search for more stuff, etc.
4. Code execution: Allow running code, which is useful for data analysis.
