# GAIA Benchmark Agents System

This document outlines the goals and architecture of a multi-agent system designed to automatically run and evaluate the GAIA benchmark using the [openai-agents-python](https://github.com/openai/openai-agents-python) codebase and examples.

## Goals

* **Automate GAIA evaluation**: Ingest each GAIA task (media + metadata), process inputs, and output a structured JSONL submission.
* **Minimize hallucination**: Ground every step in real data using tools (MCP filesystem, WebSearchTool, FileSearchTool, OCR, STT, etc.).
* **Leverage examples**: Reuse patterns and code from `openai-agents-python/examples`, including:

  * `examples/mcp/filesystem_example` for file I/O via MCP
  * `examples/web_search` for `WebSearchTool`
  * `examples/file_search` for `FileSearchTool`
  * `examples/voice/static` for audio pipelines (STT)

## High-Level Architecture

```text
CoordinatorAgent
    ├─ FileRouterAgent (MCP or native I/O)
    ├─ ProcessorAgents (per file type)
    │    ├─ TextProcessorAgent (.txt, .json, .py)
    │    ├─ DocxProcessorAgent (.docx)
    │    ├─ ExcelProcessorAgent (.xls, .xlsx)
    │    ├─ PDFProcessorAgent (.pdf)
    │    ├─ ImageOCRAgent (.png, .jpg)
    │    └─ AudioSTTAgent (.wav, .mp3)
    ├─ KnowledgeAgent (QA with WebSearchTool, FileSearchTool)
    ├─ VerifierAgent (optional fact‐checking)
    └─ SubmissionWriter (JSONL output)
```

### 1. CoordinatorAgent

* Reads each line of `gaia_val.jsonl` (task\_id, Question, etc.)
* Calls FileRouterAgent → returns `(raw_bytes, file_type)`
* Dispatches to the appropriate ProcessorAgent to get plain text
* Aggregates all text into context and invokes KnowledgeAgent
* Optionally invokes VerifierAgent for low-confidence answers
* Writes out `{"task_id":..., "model_answer":..., "reasoning_trace":...}` to submission JSONL

### 2. FileRouterAgent

* Uses either:

  * **MCP filesystem** via `HostedMCPTool` (see `examples/mcp/filesystem_example`) to securely list/read `gaia_media/`
  * **Native Python I/O** + `python-magic` for MIME detection
* Ensures no hallucinated paths or contents

### 3. ProcessorAgents

Each agent wraps a specialized pipeline and exposes a `.process(raw_bytes)` API:

| Agent               | File Types             | Example Source / Tools                                 |
| ------------------- | ---------------------- | ------------------------------------------------------ |
| TextProcessorAgent  | `.txt`, `.json`, `.py` | Direct pass-through, `json.loads`                      |
| DocxProcessorAgent  | `.docx`                | `python-docx` → text (`examples/word_processor` style) |
| ExcelProcessorAgent | `.xls`, `.xlsx`        | `pandas.read_excel` → CSV/text                         |
| PDFProcessorAgent   | `.pdf`                 | `pdfplumber`/`tika` → text                             |
| ImageOCRAgent       | `.png`, `.jpg`, etc.   | Tesseract / `openai-agents-python/examples/vision`     |
| AudioSTTAgent       | `.wav`, `.mp3`, etc.   | Whisper / `examples/voice` static STT pipeline         |

### 4. KnowledgeAgent

* Instructed to “Plan → Act”:

  1. Decide if a web or file search is needed
  2. Call `WebSearchTool` (`examples/web_search`) or `FileSearchTool` (`examples/file_search`)
  3. Reflect on results, loop if necessary
  4. Emit `FINAL ANSWER: ...` per GAIA guidelines

### 5. VerifierAgent (Optional)

* Extracts named entities or claims from `model_answer`
* Re-queries via `WebSearchTool` or `FileSearchTool`
* Flags or corrects discrepancies to reduce errors

### 6. SubmissionWriter

* Uses `ItemHelpers.text_message_outputs` and custom parsing to split chain-of-thought vs. final answer
* Writes final JSONL to disk, ready for GAIA scoring

## Tools Directory Layout

```
agents/tools/
├── web_search_tool.py       # factory for WebSearchTool (user_location config)
├── file_search_tool.py      # factory for FileSearchTool (vector_store_ids, results)
├── computer_tool.py         # factory for ComputerTool & LocalShellTool
├── code_interpreter.py      # factory for CodeInterpreterTool
├── image_gen_tool.py        # factory for ImageGenerationTool
└── hosted_mcp_tool.py       # factory for HostedMCPTool (MCP server URL & params)
```

## Directory Structure

```
.
├── agents/
│   ├── coordinator.py            # CoordinatorAgent implementation
│   ├── file_router.py            # FileRouterAgent
│   ├── processors/
│   │   ├── text_processor.py
│   │   ├── docx_processor.py
│   │   ├── excel_processor.py
│   │   ├── pdf_processor.py
│   │   ├── image_ocr_agent.py
│   │   └── audio_stt_agent.py
│   ├── knowledge_agent.py        # KnowledgeAgent with WebSearchTool, FileSearchTool
│   ├── verifier_agent.py         # Optional fact-checking agent
│   └── tools/                    # OpenAI Agents SDK tool factories
│       ├── web_search_tool.py
│       ├── file_search_tool.py
│       ├── computer_tool.py
│       ├── code_interpreter.py
│       ├── image_gen_tool.py
│       └── hosted_mcp_tool.py
├── gaia_media/                   # media and JSONL data for GAIA
├── run_gaia.py                   # top-level orchestration script
└── requirements.txt              # dependencies (openai-agents-python, python-docx, etc.)
```

## References

* **openai-agents-python/examples/mcp/filesystem\_example**: secure file I/O via MCP
* **openai-agents-python/examples folder in general**
* **openai-agents-python/examples/web\_search**: WebSearchTool usage
* **openai-agents-python/examples/file\_search**: FileSearchTool usage
* **openai-agents-python/examples/voice/static**: audio STT pipelines

This blueprint will guide incremental implementation, testing, and extension of your GAIA benchmark agent system. langfristig, each component can be refined, prompt‑tuned, and instrumented with LogFire traces for full transparency.
