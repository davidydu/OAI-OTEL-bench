from __future__ import annotations

import asyncio
import json
from pathlib import Path

from agents import Runner
from agents.tracing import trace

from ..agents_lib.file_router import FileRouterAgent
from ..agents_lib.processors import choose_processor

from .agents import (
    SearchPlan,
    SearchItem,
    SearchPlan,
    SearchItem,
    planner_agent,
    search_agent,
    writer_agent,
    verifier_agent,
    evaluator_agent,
    AnswerData,
    VerificationResult,
)



class GAIAResearchManager:
    def __init__(self, media_dir: Path) -> None:
        self.media_dir = media_dir
        self.file_router = FileRouterAgent(media_dir)

    async def run(self, jsonl_path: str, out_path: str) -> None:
        """Process all tasks in ``jsonl_path`` concurrently and write results."""
        tasks = []
        with open(jsonl_path) as src:
            for line in src:
                task = json.loads(line)
                tid = task["task_id"]
                question = task["Question"]
                
                async def handle_task(tid: str, question: str) -> dict:
                    context = self._get_context(tid)
                    with trace(workflow_name=f"GAIA {tid}"):
                        answer, reasoning, verified = await self._answer(question, context)
                    return {
                        "task_id": tid,
                        "model_answer": answer,
                        "reasoning_trace": reasoning,
                        "verified": verified,
                    }

                tasks.append(asyncio.create_task(handle_task(tid, question)))

        results = await asyncio.gather(*tasks)

        with open(out_path, "w") as dst:
            for out in results:
                dst.write(json.dumps(out, ensure_ascii=False) + "\n")

    def _get_context(self, task_id: str) -> str:
        att = self.file_router.fetch(task_id)
        if att.data is None or att.mime is None:
            return ""
        processor = choose_processor(att.mime)
        try:
            text = processor.process(att)
        except Exception:
            text = ""
        return text[:30000]

    async def _answer(self, question: str, context: str) -> tuple[str, str, bool]:
        plan = await self._plan_searches(question, context)
        results = await self._perform_searches(plan, context)

        # The evaluator only gets one chance to review the initial search results
        eval_plan = await self._evaluate_results(question, results, None)
        if eval_plan.searches:
            results.extend(await self._perform_searches(eval_plan, context))

        feedback: str | None = None
        while True:
            data = await self._write_answer(question, context, results, feedback)
            verification = await self._verify_answer(question, data)
            if verification.is_correct:
                return data.answer, data.reasoning, True

            feedback = verification.feedback
            if self._format_issue(feedback):
                # Writer corrects the format with verifier feedback
                continue

            # Otherwise the answer may be wrong. Ask evaluator if more research
            # is needed before rewriting the answer.
            eval_plan = await self._evaluate_results(question, results, feedback)
            if eval_plan.searches:
                results.extend(await self._perform_searches(eval_plan, context))
            feedback = None

    async def _plan_searches(self, question: str, context: str) -> SearchPlan:
        prompt = f"Question: {question}\nContext:\n{context}"
        result = await Runner.run(planner_agent, prompt)
        return result.final_output_as(SearchPlan)


    async def _perform_searches(self, plan: SearchPlan, context: str) -> list[str]:
        tasks = [
            asyncio.create_task(self._search(item, context)) for item in plan.searches
        ]
        results = []
        for task in asyncio.as_completed(tasks):
            r = await task
            if r is not None:
                results.append(r)
        return results

    async def _search(self, item: SearchItem, context: str) -> str | None:
        prompt = f"Source: {item.source}\nQuery: {item.query}\nReason: {item.reason}"
        if item.source == "context":
            prompt += f"\nContext:\n{context}"
        try:
            result = await Runner.run(search_agent, prompt)
            return str(result.final_output)
        except Exception:
            return None

    async def _evaluate_results(
        self, question: str, summaries: list[str], feedback: str | None
    ) -> SearchPlan:
        prompt = f"Question: {question}\nCurrent summaries: {summaries}"
        if feedback:
            prompt += f"\nVerifier feedback: {feedback}"
        result = await Runner.run(evaluator_agent, prompt)
        return result.final_output_as(SearchPlan)
        return result.final_output_as(SearchPlan)

    async def _write_answer(
        self,
        question: str,
        context: str,
        summaries: list[str],
        feedback: str | None,
    ) -> AnswerData:
        input = (
            f"Question: {question}\nContext: {context}\nResearch summaries: {summaries}"
        )
        if feedback:
            input += f"\nVerifier feedback: {feedback}\nPlease correct your answer accordingly."
        result = await Runner.run(writer_agent, input)
        return result.final_output_as(AnswerData)

    async def _verify_answer(
        self, question: str, data: AnswerData
    ) -> VerificationResult:
        prompt = f"Question: {question}\nReasoning: {data.reasoning}\nFinal answer: {data.answer}"
        result = await Runner.run(verifier_agent, prompt)
        return result.final_output_as(VerificationResult)

    def _format_issue(self, feedback: str) -> bool:
        """Return True if the verifier feedback looks like a formatting issue."""
        text = feedback.lower()
        keywords = ["format", "unit", "round", "case"]
        return any(k in text for k in keywords)