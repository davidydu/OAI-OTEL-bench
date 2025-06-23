from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Sequence

from agents import Runner, ItemHelpers, trace
from agents.mcp import MCPServerStdio

from .file_router import FileRouterAgent
from .knowledge_assistant import KnowledgeAssistantAgent
from .synthesis_agent import SynthesisAgent
from .verifier_agent import VerifierAgent
from .processors.text_processor import TextProcessorAgent
from .processors.docx_processor import DocxProcessorAgent
from .processors.excel_processor import ExcelProcessorAgent
from .processors.pdf_processor import PDFProcessorAgent
from .processors.image_ocr_agent import ImageOCRAgent
from .processors.audio_stt_agent import AudioSTTAgent

PROCESSORS = {
    "text": TextProcessorAgent(),
    "docx": DocxProcessorAgent(),
    "excel": ExcelProcessorAgent(),
    "pdf": PDFProcessorAgent(),
    "image": ImageOCRAgent(),
    "audio": AudioSTTAgent(),
}


def _choose_processor(mime: str):
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


class GAIAManager:
    """Orchestrates the GAIA workflow using multiple helper agents.

    Parameters
    ----------
    media_dir:
        Directory containing GAIA media files.
    num_assistants:
        Number of knowledge assistants to run in parallel.
    num_synths:
        Number of synthesis agents creating candidate answers.
    """

    def __init__(
        self,
        media_dir: Path,
        num_assistants: int = 3,
        num_synths: int = 3,
    ) -> None:
        self.media_dir = media_dir
        self.file_router = FileRouterAgent(media_dir)
        self.assistants = [KnowledgeAssistantAgent() for _ in range(num_assistants)]
        self.synth_agents = [SynthesisAgent() for _ in range(num_synths)]
        self.verifier = VerifierAgent()

    async def run(self, jsonl_path: str, out_path: str) -> None:
        async with MCPServerStdio(
            name="GAIA Filesystem",
            params={
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", str(self.media_dir)],
            },
        ):
            with open(jsonl_path) as src, open(out_path, "w") as dst:
                for line in src:
                    task = json.loads(line)
                    tid = task["task_id"]
                    question = task["Question"]
                    span_name = f"GAIA Question {tid}"
                    with trace(span_name):
                        context = await self._get_context(tid)
                        answer, reasoning = await self._answer(question, context)
                        verified = await self.verifier.verify(answer)
                    out = {
                        "task_id": tid,
                        "model_answer": answer,
                        "reasoning_trace": reasoning,
                        "verified": verified,
                    }
                    dst.write(json.dumps(out, ensure_ascii=False) + "\n")

    async def _get_context(self, task_id: str) -> str:
        raw, mime = self.file_router.fetch(task_id)
        if raw is None or mime is None:
            return ""
        processor = _choose_processor(mime)
        text = processor.process(raw, mime)
        return text[:30000]

    async def _answer(self, question: str, context: str) -> tuple[str, str]:
        prompt = f"Question: {question}\n\nContext:\n{context}"
        # run assistants in parallel
        assist_tasks = [Runner.run(a, prompt) for a in self.assistants]
        assist_results = await asyncio.gather(*assist_tasks)
        notes = "\n".join(res.final_output.strip() for res in assist_results)

        # synthesize multiple candidate answers
        synth_tasks = [a.synthesize(question, notes) for a in self.synth_agents]
        candidates = await asyncio.gather(*synth_tasks)
        answers, reasonings = zip(*candidates)

        # choose best using verifier
        clean = [self.verifier._clean_text(a) for a in answers]
        best_index = await self.verifier.choose_best(clean)
        formatted = await self.verifier.format_answer(question, answers[best_index])
        return formatted, reasonings[best_index]