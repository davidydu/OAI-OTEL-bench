from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import cast

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
    # verifier_agent,
    evaluator_agent,
    judge_agent,
    AnswerData,
    # VerificationResult,
    JudgeResult,
)
from ..agents_lib.tools import Message, MessageContent


class GAIAResearchManager:
    def __init__(self, media_dir: Path, *, max_concurrency: int = 20) -> None:
        self.media_dir = media_dir
        self.file_router = FileRouterAgent(media_dir)
        self._sem = asyncio.Semaphore(max_concurrency)

    async def _run_limited(self, agent, prompt: str):
        """Run an agent call while respecting the concurrency limit."""
        async with self._sem:
            return await Runner.run(agent, prompt)

    async def run(self, jsonl_path: str, out_path: str) -> None:
        """Process all tasks in ``jsonl_path`` concurrently and write results."""
        tasks = []
        with open(jsonl_path) as src:
            for line in src:
                task = json.loads(line)
                tid = task["task_id"]
                question = task["Question"]

                async def handle_task(tid: str = tid, question: str = question) -> dict:
                    """Process a single GAIA task and return the result dict.

                    Any exception raised by the underlying agents is caught so that a
                    failure in one task does not cancel the remaining work.
                    """
                    try:
                        context = self._get_context(tid)
                        with trace(workflow_name=f"GAIA {tid}"):
                            answer, reasoning, verified = await self._answer(
                                question, context
                            )
                        return {
                            "task_id": tid,
                            "model_answer": answer,
                            "reasoning_trace": reasoning,
                        }
                    except Exception as exc:  # noqa: BLE001
                        # propagate the error information rather than raising
                        return {"task_id": tid, "error": str(exc)}

                tasks.append(asyncio.create_task(handle_task()))

        # gather all task results without failing on the first exception
        results = await asyncio.gather(*tasks, return_exceptions=True)

        with open(out_path, "w") as dst:
            for out in results:
                if isinstance(out, Exception):
                    out = {"error": str(out)}
                dst.write(json.dumps(out, ensure_ascii=False) + "\n")

    def _get_context(self, task_id: str) -> str:
        att = self.file_router.fetch(task_id)
        if att is None:
            return ""
        processor = choose_processor(att.mime)
        text = processor.process(att)
        return text

    async def _answer(self, question: str, context: str) -> tuple[str, str, bool]:
        plan = await self._plan_searches(question, context)
        results = await self._perform_searches(plan, context)

        # The evaluator only gets one chance to review the initial search results
        eval_plan = await self._evaluate_results(question, results, None)
        if eval_plan.searches:
            results.extend(await self._perform_searches(eval_plan, context))

        feedback: str | None = None
        writer_count = 2
        while True:
            # data = await self._write_answer(question, context, results, feedback)
            # verification = await self._verify_answer(question, data)
            # if verification.is_correct:
            #     return data.answer, data.reasoning, True

            # feedback = verification.feedback
            # if self._format_issue(feedback):
            #     # Writer corrects the format with verifier feedback
            #     continue

            # # Otherwise the answer may be wrong. Ask evaluator if more research
            # # is needed before rewriting the answer.
            answers = [
                await self._write_answer(question, context, results, feedback)
                for _ in range(writer_count)
            ]

            judge_result = await self._judge_answers(question, context, results, answers, feedback)
            if judge_result.consensus:
                reasoning = "\n".join(a.reasoning for a in answers)
                final = judge_result.final_answer or answers[0].answer
                return final, reasoning, True

            feedback = judge_result.feedback

            eval_plan = await self._evaluate_results(question, results, feedback)
            if eval_plan.searches:
                results.extend(await self._perform_searches(eval_plan, context))
                feedback = None

    async def _plan_searches(self, question: str, context: str) -> SearchPlan:
        prompt = f"Question: {question}\nContext:\n{context}"
        result = await self._run_limited(planner_agent, prompt)
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
        prompt = (
            f"Source: {item.source}\nQuery: {item.query}\nReason: {item.reason}"
            f"\nContext:\n{context}"
        )
        try:
            result = await self._run_limited(search_agent, prompt)
            return str(result.final_output)
        except Exception:
            return None

    async def _evaluate_results(
        self, question: str, summaries: list[str], feedback: str | None
    ) -> SearchPlan:
        prompt = f"Question: {question}\nCurrent summaries: {summaries}"
        if feedback:
            prompt += f"\nJudge feedback: {feedback}"
        result = await self._run_limited(evaluator_agent, prompt)
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
            input += f"\nJudge feedback: {feedback}\nPlease correct your answer accordingly."
        attempt = 0
        while True:
            result = await self._run_limited(writer_agent, input)
            try:
                return result.final_output_as(AnswerData)
            except Exception:  # noqa: BLE001
                attempt += 1
                if attempt >= 3:
                    raise
                # Request the writer to correct the formatting on retry
                input += (
                    "\nThe previous response was not valid JSON. "
                    "Please return only a JSON object with 'reasoning' and "
                    "'answer' fields."
                )

    # async def _verify_answer(
    #     self, question: str, data: AnswerData
    # ) -> VerificationResult:
    #     PROMPT = (
    #         "Check that the answer field satisfies the following requirements: "
    #         "The answer should be a number OR as few words as possible OR a comma separated list of numbers and/or strings. "
    #         "If asked for a number, don't use comma to write your number neither use units such as $ or percent sign unless specified otherwise. \
    #         If asked for a string, don't use articles, neither abbreviations (e.g. for cities), and write the digits in plain text unless specified otherwise. \
    #         If asked for a comma separated list, apply the above rules depending of whether the element to be put in the list is a number or a string. "
    #         "There is no requirement for the format of the reasoning trace. Don't worry about the reasoning trace at all."
    #     )

    #     query = [
    #         Message(role="system", content=[MessageContent(type="text", text=PROMPT)]),
    #         Message(role="user", content=[MessageContent(type="text", text=question)]),
    #     ]
    #     response = [
    #         Message(
    #             role="writer agent",
    #             content=[
    #                 MessageContent(type="text", text=data.reasoning),
    #                 MessageContent(type="text", text=data.answer),
    #             ],
    #         )
    #     ]
        
    #     verifier_input = json.dumps(
    #         {
    #             "query": [m.model_dump() for m in query],
    #             "response": [m.model_dump() for m in response],
    #             "tool_definitions": None,
    #         }
    #     )

    #     result = await self._run_limited(verifier_agent, verifier_input)
    #     data = result.final_output
    #     if isinstance(data, str):
    #         try:
    #             data = VerificationResult.model_validate_json(data)
    #         except Exception:
    #             data = VerificationResult(score=0, feedback="", is_correct=False)

    #     return cast(VerificationResult, data)

    async def _judge_answers(
        self,
        question: str,
        context: str,
        summaries: list[str],
        answers: list[AnswerData],
        feedback: str | None,
    ) -> JudgeResult:
        prompt = (
            f"Question: {question}\nContext: {context}\nResearch summaries: {summaries}"
            f"\nAnswers: {[{'reasoning': a.reasoning, 'answer': a.answer} for a in answers]}"
        )
        if feedback:
            prompt += f"\nPrevious feedback: {feedback}"
        result = await self._run_limited(judge_agent, prompt)
        return result.final_output_as(JudgeResult)
        
    # def _format_issue(self, feedback: str) -> bool:
    #     """Return True if the verifier feedback looks like a formatting issue."""
    #     text = feedback.lower()
    #     keywords = ["format", "unit", "round", "case"]
    #     return any(k in text for k in keywords)

