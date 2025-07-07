from __future__ import annotations

import json
import re
import string
import sys
import warnings
from pathlib import Path
from typing import List, Optional


def normalize_number_str(number_str: str) -> float:
    for char in ("$", "%", ","):
        number_str = number_str.replace(char, "")
    try:
        return float(number_str)
    except ValueError:
        return float("inf")


def split_string(s: str, char_list: List[str] = [",", ";"]) -> List[str]:
    return re.split(f"[{''.join(char_list)}]", s)


def normalize_str(input_str: str, *, remove_punct: bool = True) -> str:
    out = re.sub(r"\s", "", input_str)
    if remove_punct:
        out = out.translate(str.maketrans("", "", string.punctuation))
    return out.lower()


def question_scorer(model_answer: Optional[str], ground_truth: str) -> bool:
    def is_float(x: str) -> bool:
        try:
            float(x)
            return True
        except ValueError:
            return False

    model_answer = model_answer or "None"

    if is_float(ground_truth):
        return normalize_number_str(model_answer) == float(ground_truth)

    if any(c in ground_truth for c in (",", ";")):
        gt_elems = split_string(ground_truth)
        ma_elems = split_string(model_answer)
        if len(gt_elems) != len(ma_elems):
            return False
        return all(
            normalize_number_str(ma) == float(gt)
            if is_float(gt)
            else normalize_str(ma, remove_punct=False)
            == normalize_str(gt, remove_punct=False)
            for ma, gt in zip(ma_elems, gt_elems)
        )

    return normalize_str(model_answer) == normalize_str(ground_truth)


def evaluate(submission_path: str, reference_path: str) -> None:
    submission = {
        json.loads(l)["task_id"]: json.loads(l).get("model_answer")
        for l in Path(submission_path).read_text().splitlines()
        if l.strip()
    }
    reference, questions = {}, {}
    for line in Path(reference_path).read_text().splitlines():
        if not line.strip():
            continue
        obj = json.loads(line)
        reference[obj["task_id"]] = obj["Final answer"]
        questions[obj["task_id"]] = obj.get("Question", "")

    total = len(reference)
    correct = 0
    wrong = []

    for tid, gt in reference.items():
        pred = submission.get(tid)
        if question_scorer(pred, gt):
            correct += 1
        else:
            wrong.append((tid, questions.get(tid, ""), pred, gt))

    acc = 100.0 * correct / total if total else 0.0
    print(f"Accuracy: {acc:.2f}% ({correct}/{total})\n")

    if wrong:
        print("Mismatches:")
        for tid, q, pred, gt in wrong:
            print(f"- Task ID    : {tid}")
            if q:
                print(f"  Question   : {q}")
            print(f"  Submission : {pred!r}")
            print(f"  Reference  : {gt!r}")
        print()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        prog = Path(sys.argv[0]).name
        print(f"Usage: python {prog} SUBMISSION_JSONL REFERENCE_JSONL")
        sys.exit(1)
    evaluate(sys.argv[1], sys.argv[2])
