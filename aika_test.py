from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path
from typing import Any


DEFAULT_QUESTIONS_FILE = Path(__file__).with_name("questions_211.json")
RANDOM_SET_SIZE = 50

RESET = "\033[0m"
GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"


def colorize(text: str, color: str) -> str:
    return f"{color}{text}{RESET}"


def info(text: str) -> str:
    return colorize(text, YELLOW)


def success(text: str) -> str:
    return colorize(text, GREEN)


def failure(text: str) -> str:
    return colorize(text, RED)


def resolve_questions_file(raw_path: str | None) -> Path:
    if not raw_path:
        return DEFAULT_QUESTIONS_FILE

    candidate = Path(raw_path)
    if candidate.exists():
        return candidate

    local_candidate = Path(__file__).with_name(raw_path)
    if local_candidate.exists():
        return local_candidate

    return candidate


def load_questions(questions_file: Path) -> list[dict[str, Any]]:
    if not questions_file.exists():
        raise FileNotFoundError(f"Cannot find questions file: {questions_file}")

    data = json.loads(questions_file.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("Questions file must contain a JSON array.")

    return data


def build_question_map(questions: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    qmap: dict[int, dict[str, Any]] = {}
    for item in questions:
        qid = item.get("id")
        if isinstance(qid, int):
            qmap[qid] = item
    return qmap


def get_last_question_id(question_map: dict[int, dict[str, Any]]) -> int:
    if not question_map:
        raise ValueError("Questions file does not contain any valid question IDs.")
    return max(question_map)


def ask_menu_choice() -> str:
    print(info("Choose mode:"))
    print(info("1 - Work with questions from 1 to N"))
    print(info("2 - Work with questions from A to B"))
    print(info("3 - 50 random questions from 1 to N"))

    while True:
        choice = input(info("Enter 1, 2 or 3: ")).strip()
        if choice in {"1", "2", "3"}:
            return choice
        print(failure("Invalid mode. Please enter 1, 2, or 3."))


def ask_upper_bound(last_question_id: int) -> int:
    while True:
        raw = input(info(f"Enter N (from 2 to {last_question_id}): ")).strip()
        if not raw.isdigit():
            print(failure("Please enter a valid integer."))
            continue

        value = int(raw)
        if 2 <= value <= last_question_id:
            return value
        print(failure(f"N must be between 2 and {last_question_id}."))


def ask_range(last_question_id: int) -> tuple[int, int]:
    while True:
        raw = input(info(f"Enter range as A,B (both from 1 to {last_question_id}): ")).strip()
        parts = [part.strip() for part in raw.split(",")]
        if len(parts) != 2 or not all(part.isdigit() for part in parts):
            print(failure("Please enter two integers separated by a comma, e.g. 10,40."))
            continue

        start, end = int(parts[0]), int(parts[1])
        if not (1 <= start <= last_question_id and 1 <= end <= last_question_id):
            print(failure(f"Both numbers must be between 1 and {last_question_id}."))
            continue
        if start >= end:
            print(failure("The first number must be less than the second."))
            continue

        return start, end


def ask_random_pool_upper_bound(last_question_id: int) -> int:
    while True:
        raw = input(info(f"Enter N for random mode (minimum {RANDOM_SET_SIZE}, maximum {last_question_id}): ")).strip()
        if not raw.isdigit():
            print(failure("Please enter a valid integer."))
            continue

        value = int(raw)
        if RANDOM_SET_SIZE <= value <= last_question_id:
            return value
        print(failure(f"N must be between {RANDOM_SET_SIZE} and {last_question_id}."))


def choose_question_ids(choice: str, last_question_id: int) -> list[int]:
    if choice == "1":
        upper = ask_upper_bound(last_question_id)
        ids = list(range(1, upper + 1))
    elif choice == "2":
        start, end = ask_range(last_question_id)
        ids = list(range(start, end + 1))
    else:
        upper = ask_random_pool_upper_bound(last_question_id)
        ids = random.sample(range(1, upper + 1), RANDOM_SET_SIZE)

    random.shuffle(ids)
    return ids


def get_correct_answers_text(answers: list[dict[str, Any]]) -> str:
    correct_texts = [str(ans.get("text", "")).strip() for ans in answers if ans.get("correct")]
    return " | ".join(text for text in correct_texts if text) or "(No correct answer found)"


def ask_answer_index(num_answers: int) -> int:
    letters = [chr(ord("A") + i) for i in range(num_answers)]
    allowed = set(letters)

    while True:
        picked = input(info("Your answer (letter): ")).strip().upper()
        if picked in allowed:
            return letters.index(picked)
        print(failure(f"Invalid answer. Choose one of: {', '.join(letters)}"))


def run_quiz(question_ids: list[int], question_map: dict[int, dict[str, Any]]) -> None:
    wrong_items: list[dict[str, str]] = []
    correct_count = 0

    for idx, qid in enumerate(question_ids, start=1):
        question = question_map.get(qid)
        if question is None:
            print(failure(f"\nSkipping question {qid}: not found in JSON."))
            continue

        qtext = str(question.get("question", "")).strip()
        answers = question.get("answers", [])
        if not isinstance(answers, list) or len(answers) < 2:
            print(failure(f"\nSkipping question {qid}: invalid answers format."))
            continue

        shuffled_answers = [dict(ans) for ans in answers]
        random.shuffle(shuffled_answers)

        print(info(f"\n[{idx}/{len(question_ids)}] Question ID {qid}"))
        print(info(qtext))

        for a_idx, answer in enumerate(shuffled_answers):
            label = chr(ord("A") + a_idx)
            print(info(f"{label}) {str(answer.get('text', '')).strip()}"))

        picked_index = ask_answer_index(len(shuffled_answers))
        picked_answer = shuffled_answers[picked_index]
        picked_text = str(picked_answer.get("text", "")).strip()
        is_correct = bool(picked_answer.get("correct"))
        right_text = get_correct_answers_text(shuffled_answers)

        if is_correct:
            correct_count += 1
            print(success("Correct!"))
        else:
            print(failure("Incorrect."))
            print(success(f"Right answer: {right_text}"))
            wrong_items.append(
                {
                    "id": str(qid),
                    "question": qtext,
                    "your": picked_text,
                    "right": right_text,
                }
            )

    total_answered = correct_count + len(wrong_items)
    print(info("\n=== Result ==="))
    print(info(f"Score: {correct_count}/{total_answered}"))

    if not wrong_items:
        print(success("All answers were correct."))
        return

    print(failure("\nIncorrect answers list:"))
    for item in wrong_items:
        print(failure(f"- ID {item['id']}: {item['question']}"))
        print(failure(f"  Your answer: {item['your']}"))
        print(success(f"  Right answer: {item['right']}"))


def main() -> None:
    random.seed()

    parser = argparse.ArgumentParser(description="Run CLI medical test quizzes from a JSON question bank.")
    parser.add_argument(
        "questions_file",
        nargs="?",
        help="Path to a JSON file like questions_211.json or questions_100.json",
    )
    args = parser.parse_args()

    questions_file = resolve_questions_file(args.questions_file)

    try:
        questions = load_questions(questions_file)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        print(failure(str(exc)))
        sys.exit(1)

    question_map = build_question_map(questions)
    last_question_id = get_last_question_id(question_map)

    if last_question_id < 2:
        print(failure("The selected question file must contain at least 2 questions."))
        sys.exit(1)

    print(info(f"Loaded: {questions_file.name}"))
    print(info(f"Available question IDs: 1 to {last_question_id}"))

    choice = ask_menu_choice()
    selected_ids = choose_question_ids(choice, last_question_id)
    run_quiz(selected_ids, question_map)


if __name__ == "__main__":
    main()