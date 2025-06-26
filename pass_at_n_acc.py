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


def load_reference(path: Path) -> dict:
    """Load reference answers from GAIA metadata.jsonl."""
    refs = {}
    with path.open('r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            obj = json.loads(line)
            refs[obj['task_id']] = obj['Final answer']
    return refs


def compute_pass_at_n(ref_path: Path, prefix: Path, n: int) -> None:
    reference = load_reference(ref_path)
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
    for task_id, ref_ans in reference.items():
        if any(run.get(task_id) == ref_ans for run in runs):
            correct += 1

    accuracy = (correct / total * 100) if total else 0.0
    print(f"Pass@{n} accuracy: {accuracy:.2f}% ({correct}/{total})")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(f"Usage: python {sys.argv[0]} REFERENCE_JSONL RUN_PREFIX N")
        print("RUN_PREFIX should be the path without the _1.jsonl suffix")
        sys.exit(1)

    reference_jsonl = Path(sys.argv[1])
    run_prefix = Path(sys.argv[2])
    try:
        n = int(sys.argv[3])
    except ValueError:
        print("N must be an integer")
        sys.exit(1)

    compute_pass_at_n(reference_jsonl, run_prefix, n)