import json
from pathlib import Path
import sys


def load_answers(path: Path) -> dict:
    """Load answers from a submission jsonl file."""
    answers = {}
    with path.open('r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            obj = json.loads(line)
            answers[obj['task_id']] = obj.get('model_answer')
    return answers


def load_reference(path: Path) -> tuple[dict, dict]:
    """Load reference answers and questions from GAIA metadata.jsonl."""
    refs = {}
    questions = {}
    with path.open('r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            obj = json.loads(line)
            refs[obj["task_id"]] = obj["Final answer"]
            questions[obj["task_id"]] = obj.get("Question", "")
    return refs, questions


def compute_pass_at_n(ref_path: Path, prefix: Path, n: int, output: Path | None = None) -> None:
    reference, questions = load_reference(ref_path)
    runs = []
    for i in range(1, n + 1):
        run_file = prefix.parent / f"{prefix.stem}_{i}.jsonl"
        if run_file.exists():
            runs.append(load_answers(run_file))
        else:
            print(f"Warning: {run_file} not found")
            runs.append({})

    total = len(reference)
    correct = 0
    wrong = []
    for task_id, ref_ans in reference.items():
        if any(run.get(task_id) == ref_ans for run in runs):
            correct += 1
        else:
            sample = None
            for run in runs:
                if task_id in run:
                    sample = run[task_id]
                    break
            wrong.append((task_id, questions.get(task_id, ""), sample, ref_ans))

    accuracy = (correct / total * 100) if total else 0.0
    
    lines = [f"Accuracy: {accuracy:.2f}% ({correct}/{total})", ""]
    if wrong:
        lines.append("Mismatches:")
        for task_id, question, sub_ans, corr_ans in wrong:
            lines.append(f"- Task ID: {task_id}")
            if question:
                lines.append(f"    Question: {question}")
            lines.append(f"    Submission: {sub_ans!r}")
            lines.append(f"    Reference : {corr_ans!r}")
    report = "\n".join(lines)

    print(report)

    if output:
        output.write_text(report + "\n", encoding="utf-8")



if __name__ == "__main__":
    if len(sys.argv) not in {4, 5}:
        print(
            f"Usage: python {sys.argv[0]} REFERENCE_JSONL RUN_PREFIX N [OUTPUT_TXT]"
        )
        print("RUN_PREFIX should be the path without the _1.jsonl suffix")
        sys.exit(1)

    reference_jsonl = Path(sys.argv[1])
    run_prefix = Path(sys.argv[2])
    try:
        n = int(sys.argv[3])
    except ValueError:
        print("N must be an integer")
        sys.exit(1)

    output_path = Path(sys.argv[4]) if len(sys.argv) == 5 else None

    compute_pass_at_n(reference_jsonl, run_prefix, n, output_path)