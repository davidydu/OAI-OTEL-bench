from __future__ import annotations

import json
import os
from pathlib import Path

import logfire
from agents import Runner, ItemHelpers, trace
from agents.mcp import MCPServerStdio

from agents.file_router import FileRouterAgent
from agents.processors.text_processor import TextProcessorAgent
from agents.processors.docx_processor import DocxProcessorAgent
from agents.processors.excel_processor import ExcelProcessorAgent
from agents.processors.pdf_processor import PDFProcessorAgent
from agents.processors.image_ocr_agent import ImageOCRAgent
from agents.processors.audio_stt_agent import AudioSTTAgent
from agents.knowledge_agent import KnowledgeAgent
from agents.verifier_agent import VerifierAgent


logfire.configure()
logfire.instrument_httpx()
logfire.instrument_openai_agents()


PROCESSORS = {
    "text": TextProcessorAgent(),
    "docx": DocxProcessorAgent(),
    "excel": ExcelProcessorAgent(),
    "pdf": PDFProcessorAgent(),
    "image": ImageOCRAgent(),
    "audio": AudioSTTAgent(),
}


def choose_processor(mime: str):
    if mime.startswith("text/") or "json" in mime or "python" in mime:
        return PROCESSORS["text"]
    if "word" in mime:
        return PROCESSORS["docx"]
    if "excel" in mime or "spreadsheet" in mime:
        return PROCESSORS["excel"]
    if "pdf" in mime:
        return PROCESSORS["pdf"]
    if mime.startswith("image/"):
        return PROCESSORS["image"]
    if mime.startswith("audio/"):
        return PROCESSORS["audio"]
    return PROCESSORS["text"]


async def main(jsonl_path: str, out_path: str) -> None:
    media_dir = Path("gaia_media").resolve()
    async with MCPServerStdio(
        name="GAIA Filesystem",
        params={
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", str(media_dir)],
        },
    ):
        file_router = FileRouterAgent(media_dir)
        knowledge_agent = KnowledgeAgent()
        verifier_agent = VerifierAgent()

        with open(jsonl_path) as src, open(out_path, "w") as dst:
            for line in src:
                task = json.loads(line)
                tid = task["task_id"]
                question = task["Question"]
                span = f"GAIA Question {tid}"

                with trace(span):
                    raw, mime = file_router.fetch(tid)
                    processor = choose_processor(mime)
                    context = processor.process(raw, mime)
                    context = context[:30000]
                    result = Runner.run_sync(
                        knowledge_agent,
                        f"Question: {question}\n\nContext:\n{context}",
                    )

                text = "\n".join(ItemHelpers.text_message_outputs(result.new_items)).strip()
                if "FINAL ANSWER:" in text:
                    reasoning, final = text.rsplit("FINAL ANSWER:", 1)
                else:
                    reasoning, final = text, ""
                verified = verifier_agent.verify(final.strip())

                out = {
                    "task_id": tid,
                    "model_answer": final.strip(),
                    "reasoning_trace": reasoning.strip(),
                    "verified": verified,
                }
                dst.write(json.dumps(out, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    import asyncio
    import sys

    if len(sys.argv) != 3:
        print("Usage: python run_gaia.py metadata.jsonl submission.jsonl")
        raise SystemExit(1)

    asyncio.run(main(sys.argv[1], sys.argv[2]))
