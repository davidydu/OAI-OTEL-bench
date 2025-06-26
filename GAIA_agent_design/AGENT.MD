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
    ├─ FileRouterAgent          # secure file I/O via MCP or native code
    ├─ ProcessorAgents          # format-specific parsing → plain text
    │    ├─ TextProcessorAgent  # .txt, .json, .py
    │    ├─ DocxProcessorAgent  # .docx          (python-docx)
    │    ├─ ExcelProcessorAgent # .xls/.xlsx     (pandas)
    │    ├─ PDFProcessorAgent   # .pdf           (pdfplumber + vision fallback)
    │    ├─ PPTXProcessorAgent  # .pptx          (python-pptx)
    │    ├─ PDBProcessorAgent   # .pdb           (biopython)
    │    ├─ ZipProcessorAgent   # .zip           (extract + text)
    │    ├─ ImageOCRAgent       # .png/.jpg      (GPT‑4o vision with OCR fallback)
    │    └─ AudioSTTAgent       # .wav/.mp3      (Whisper / cloud STT)
    ├─ KnowledgeAgent           # QA: Plan→Act→Reflect with search/file tools
    ├─ WriteAgent               # Formats answer and reasoning into GAIA-spec JSONL
    ├─ VerifierAgent            # Post-write format & correctness check
    └─ SubmissionWriter         # Persists final JSONL submission
```

### Expanded Flow

1. **CoordinatorAgent** kicks off a run for each question: reads metadata, invokes FileRouterAgent and ProcessorAgents, and collects all extracted text.

2. **KnowledgeAgent** receives the question + aggregated context, performs searches or file lookups as needed, and outputs a candidate `FINAL ANSWER:` plus reasoning trace.

3. **WriteAgent** takes the raw model output and serializes it into the GAIA JSONL schema, splitting out `model_answer` and `reasoning_trace`.

4. **VerifierAgent** consumes the written JSONL entry, inspects both the `reasoning_trace` and the `model_answer`, and checks:

   * **Format compliance** (units, rounding, number vs string, comma use)
   * **Consistency** (answer matches reasoning, no contradictions)
   * **Basic correctness** (e.g. re-calculate simple numeric steps or re-run unit conversions)

   If a violation is detected, it can:

   * Flag the entry for retry
   * Auto-correct minor format or rounding mistakes
   * Append a `verified: false` tag or add a corrective note

5. **SubmissionWriter** finalizes and writes out the verified (or flagged) JSONL submission ready for GAIA scoring.

### Additional Accuracy Mechanisms

* **Dual-pass verification**: run a second, lightweight agent to independently answer the same question and compare outputs.
* **Regex-based format enforcement**: define strict patterns for numeric answers (e.g. `^\d+(\.\d{1,2})?$` for two-decimal numbers) and reject mismatches.
* **Confidence thresholds**: leverage LLM token probabilities or explicit “I am confident at X%” statements to decide when to trigger a human review or retrial.
* **Cache and dedupe**: store past question-answer pairs to avoid re-computation and reduce rate-limit errors.
* **Human-in-the-loop checkpointing**: for Level 4–5 tasks, insert manual validation steps where high stakes demand it.
* **Ensemble scoring**: aggregate answers from multiple model variants or prompt templates, then pick the majority or highest-confidence response.

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

### Media processing pipeline

Media files are handled according to type:

* **Images (PNG/JPEG):** sent directly to GPT‑4o via `ImageVisionAgent` which returns OCR text or a brief description.
* **PDFs:** uploaded to the vision API with `PDFVisionAgent` so the model can read native text or scanned pages.
* **Audio:** processed with Whisper in `AudioSTTAgent`.
* **Other formats:** converted to plain text using the corresponding processor (docx, pptx, spreadsheets, archives, etc.).

The resulting text or summary is then used as context for the planner agent.
