#!/usr/bin/env python3
"""
Compute pass-at-N accuracy for GAIA-style JSONL runs, using an enhanced
answer-equality test that supports numeric normalization, multi-answer
lists, and punctuation/whitespace insensitivity.

Usage:
    python compute_pass_at_n.py REFERENCE_JSONL RUN_PREFIX N [OUTPUT_TXT]

`RUN_PREFIX` is the common filename stem for the runs, **without**
the “_1.jsonl” suffix.  For example, if you have

    my_run_1.jsonl
    my_run_2.jsonl
    my_run_3.jsonl

then pass `my_run` as the prefix and `N=3`.
"""
from __future__ import annotations

import json
import re
import string
import sys
import warnings
from pathlib import Path
from typing import List, Optional


# --------------------------------------------------------------------------- #
# Enhanced comparison helpers (from the GAIA evaluation script)
# --------------------------------------------------------------------------- #
def normalize_number_str(number_str: str) -> float:
    """Convert a string to a float after stripping $, %, and commas."""
    for char in ("$", "%", ","):
        number_str = number_str.replace(char, "")
    try:
        return float(number_str)
    except ValueError:
        return float("inf")


def split_string(s: str, char_list: List[str] = [",", ";"]) -> List[str]:
    """Split on comma/semicolon for multi-answer ground truths."""
    return re.split(f"[{''.join(char_list)}]", s)


def normalize_str(input_str: str, *, remove_punct: bool = True) -> str:
    """Lowercase and strip whitespace (and optionally punctuation)."""
    out = re.sub(r"\s", "", input_str or "")
    if remove_punct:
        out = out.translate(str.maketrans("", "", string.punctuation))
    return out.lower()


def question_scorer(model_answer: Optional[str], ground_truth: str) -> bool:
    """Return True iff `model_answer` matches `ground_truth` under GAIA rules."""
    def is_float(x: str) -> bool:
        try:
            float(x)
            return True
        except ValueError:
            return False

    model_answer = model_answer or "None"

    # Pure numeric comparison
    if is_float(ground_truth):
        return normalize_number_str(model_answer) == float(ground_truth)

    # Multi-element list (comma- or semicolon-separated)
    if any(c in ground_truth for c in (",", ";")):
        gt_elems = split_string(ground_truth)
        ma_elems = split_string(model_answer)
        if len(gt_elems) != len(ma_elems):
            return False
        return all(
            normalize_number_str(ma) == float(gt) if is_float(gt)
            else normalize_str(ma, remove_punct=False) == normalize_str(gt, remove_punct=False)
            for ma, gt in zip(ma_elems, gt_elems)
        )

    # Default string normalization
    return normalize_str(model_answer) == normalize_str(ground_truth)


# --------------------------------------------------------------------------- #
# I/O helpers (unchanged except for typing tweaks)
# --------------------------------------------------------------------------- #
def load_answers(path: Path) -> dict[str, Optional[str]]:
    """Load answers from one submission JSONL file."""
    answers: dict[str, Optional[str]] = {}
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            obj = json.loads(line)
            answers[obj["task_id"]] = obj.get("model_answer")
    return answers


def load_reference(path: Path) -> tuple[dict[str, str], dict[str, str]]:
    """Load reference answers and questions from GAIA metadata.jsonl."""
    refs: dict[str, str] = {}
    questions: dict[str, str] = {}
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            obj = json.loads(line)
            refs[obj["task_id"]] = obj["Final answer"]
            questions[obj["task_id"]] = obj.get("Question", "")
    return refs, questions


# --------------------------------------------------------------------------- #
# Main evaluation logic
# --------------------------------------------------------------------------- #
def compute_pass_at_n(
    ref_path: Path,
    prefix: Path,
    n: int,
    output: Path | None = None,
) -> None:
    """Compute pass-at-N where *any* of N runs may satisfy the scorer."""
    reference, questions = load_reference(ref_path)

    # Load all available runs (run_1.jsonl … run_n.jsonl).
    runs: list[dict[str, Optional[str]]] = []
    for i in range(1, n + 1):
        run_file = prefix.parent / f"{prefix.stem}_{i}.jsonl"
        if run_file.exists():
            runs.append(load_answers(run_file))
        else:
            warnings.warn(f"{run_file} not found — treating as empty run.")
            runs.append({})

    total = len(reference)
    correct = 0
    wrong: list[tuple[str, str, Optional[str], str]] = []

    for task_id, gt in reference.items():
        # Pass if *any* run matches according to question_scorer().
        if any(
            question_scorer(run.get(task_id), gt)
            for run in runs
        ):
            correct += 1
        else:
            # Find a representative prediction (first non-None we see).
            sample_pred: Optional[str] = None
            for run in runs:
                if task_id in run:
                    sample_pred = run[task_id]
                    break
            wrong.append((task_id, questions.get(task_id, ""), sample_pred, gt))

    accuracy = 100.0 * correct / total if total else 0.0

    # --------------------------------------------------------------------- #
    # Reporting
    # --------------------------------------------------------------------- #
    lines: list[str] = [
        f"Accuracy: {accuracy:.2f}% ({correct}/{total})",
        "",
    ]
    if wrong:
        lines.append("Mismatches:")
        for tid, q, pred, gt in wrong:
            lines.append(f"- Task ID    : {tid}")
            if q:
                lines.append(f"  Question   : {q}")
            lines.append(f"  Submission : {pred!r}")
            lines.append(f"  Reference  : {gt!r}")
    report = "\n".join(lines)

    print(report)
    if output:
        output.write_text(report + "\n", encoding="utf-8")


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    if len(sys.argv) not in {4, 5}:
        prog = Path(sys.argv[0]).name
        print(f"Usage: python {prog} REFERENCE_JSONL RUN_PREFIX N [OUTPUT_TXT]")
        print("RUN_PREFIX should be the path without the _1.jsonl suffix")
        sys.exit(1)

    reference_jsonl = Path(sys.argv[1])
    run_prefix = Path(sys.argv[2])

    try:
        n_runs = int(sys.argv[3])
    except ValueError:
        print("N must be an integer")
        sys.exit(1)

    out_path = Path(sys.argv[4]) if len(sys.argv) == 5 else None
    compute_pass_at_n(reference_jsonl, run_prefix, n_runs, out_path)
