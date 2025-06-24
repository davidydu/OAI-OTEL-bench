import json
import sys

def evaluate(submission_path: str, reference_path: str):
    # Load submission answers
    submission = {}
    with open(submission_path, 'r', encoding='utf-8') as f:
        for line in f:
            obj = json.loads(line)
            submission[obj["task_id"]] = obj["model_answer"]

    # Load reference answers and questions
    reference = {}
    questions = {}
    with open(reference_path, 'r', encoding='utf-8') as f:
        for line in f:
            obj = json.loads(line)
            reference[obj["task_id"]] = obj["Final answer"]
            questions[obj["task_id"]] = obj.get("Question", "")

    # Compare
    total = len(reference)
    correct = 0
    wrong = []

    for task_id, correct_ans in reference.items():
        sub_ans = submission.get(task_id)
        if sub_ans == correct_ans:
            correct += 1
        else:
            wrong.append((task_id, questions.get(task_id), sub_ans, correct_ans))

    accuracy = correct / total * 100 if total else 0.0

    # Report
    print(f"Accuracy: {accuracy:.2f}% ({correct}/{total})\n")

    if wrong:
        print("Mismatches:")
        for task_id, question, sub_ans, corr_ans in wrong:
            print(f"- Task ID: {task_id}")
            if question:
                print(f"    Question: {question}")
            print(f"    Submission: {sub_ans!r}")
            print(f"    Reference : {corr_ans!r}")
        print()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: python {sys.argv[0]} SUBMISSION_JSONL REFERENCE_JSONL")
        sys.exit(1)
    evaluate(sys.argv[1], sys.argv[2])