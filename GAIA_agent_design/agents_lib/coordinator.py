from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from agents import Agent, Runner, handoff, ItemHelpers

from .file_router import FileRouterAgent
from .knowledge_agent import KnowledgeAgent
from .verifier_agent import VerifierAgent
from .research_assistant import ResearchAssistantAgent
from .processors.text_processor import TextProcessorAgent
from .processors.docx_processor import DocxProcessorAgent
from .processors.excel_processor import ExcelProcessorAgent
from .processors.pdf_processor import PDFProcessorAgent
from .processors.image_ocr_agent import ImageOCRAgent
from .processors.audio_stt_agent import AudioSTTAgent


@dataclass
class TaskResult:
    task_id: str
    model_answer: str
    reasoning_trace: str
    verified: str


COORDINATOR_PROMPT = (
    "You are the CoordinatorAgent. Delegate research to the assistants via their"
    " handoff tools. After collecting their notes, optionally use the verifier"
    " agent, then synthesize the best final answer. End with 'FINAL ANSWER:'"
)


class CoordinatorAgent(Agent):
    def __init__(self, media_dir: str | Path, num_assistants: int = 2) -> None:
        self.file_router = FileRouterAgent(media_dir)
        self.processors = {
            "text": TextProcessorAgent(),
            "docx": DocxProcessorAgent(),
            "excel": ExcelProcessorAgent(),
            "pdf": PDFProcessorAgent(),
            "image": ImageOCRAgent(),
            "audio": AudioSTTAgent(),
        }

        self.assistants = [
            ResearchAssistantAgent(name=f"Assistant{i+1}")
            for i in range(num_assistants)
        ]
        self.verifier = VerifierAgent()

        handoffs_list = [handoff(a) for a in self.assistants]
        handoffs_list.append(handoff(self.verifier))
        super().__init__(
            name="CoordinatorAgent",
            instructions=COORDINATOR_PROMPT,
            handoffs=handoffs_list,
        )

    def choose_processor(self, mime: str):
        if mime.startswith("text/") or "json" in mime or "python" in mime:
            return self.processors["text"]
        if "word" in mime:
            return self.processors["docx"]
        if "excel" in mime or "spreadsheet" in mime:
            return self.processors["excel"]
        if "pdf" in mime:
            return self.processors["pdf"]
        if mime.startswith("image/"):
            return self.processors["image"]
        if mime.startswith("audio/"):
            return self.processors["audio"]
        return self.processors["text"]

    async def run_task(self, task: dict) -> TaskResult:
        tid = task["task_id"]
        question = task["Question"]
        raw, mime = self.file_router.fetch(tid)
        if raw is not None and mime is not None:
            processor = self.choose_processor(mime)
            context = processor.process(raw, mime)
        else:
            context = ""
        context = context[:30000]

        # Run assistants in parallel
        assist_prompts = [
            f"Question: {question}\n\nContext:\n{context}" for _ in self.assistants
        ]
        assistant_runs = [
            Runner.run(a, p) for a, p in zip(self.assistants, assist_prompts)
        ]
        assistant_results = await asyncio.gather(*assistant_runs)
        notes: list[str] = []
        for result in assistant_results:
            notes.append(
                "\n".join(ItemHelpers.text_message_outputs(result.new_items)).strip()
            )

        synth_prompt = (
            f"Question: {question}\n"
            + "\n".join(f"Assistant {i+1} notes:\n{n}" for i, n in enumerate(notes))
            + "\nProvide the best answer.\nFINAL ANSWER:"
        )
        final_run = await Runner.run(self, synth_prompt)
        text = "\n".join(ItemHelpers.text_message_outputs(final_run.new_items)).strip()
        if "FINAL ANSWER:" in text:
            reasoning, final = text.rsplit("FINAL ANSWER:", 1)
        else:
            reasoning, final = text, ""

        verified = await self.verifier.verify(final.strip())
        return TaskResult(tid, final.strip(), reasoning.strip(), verified)
