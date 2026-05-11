#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exam Prep CLI — ОП11 Безопасность жизнедеятельности
Дербентский медицинский колледж им. Г.А. Илизарова
"""

import json
import random
import os
import sys

# ─── Paths ────────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
QUESTIONS_FILE = os.path.join(SCRIPT_DIR, "questions.json")

# ─── Colors ───────────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def load_questions():
    with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def get_correct_ids(q):
    return [a["id"] for a in q["answers"] if a["correct"]]

def get_correct_texts(q):
    return [a["text"] for a in q["answers"] if a["correct"]]

def print_header():
    print(f"{CYAN}{BOLD}")
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║     ОП11 — БЕЗОПАСНОСТЬ ЖИЗНЕДЕЯТЕЛЬНОСТИ                  ║")
    print("║     Подготовка к промежуточной аттестации                   ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print(RESET)

def choose_mode(total):
    print(f"{BOLD}Выберите режим тестирования:{RESET}\n")
    print(f"  {CYAN}1{RESET}  — От 1 до N  (случайный порядок вопросов 1..N)")
    print(f"  {CYAN}2{RESET}  — От N до M  (случайный порядок вопросов N..M)")
    print(f"  {CYAN}3{RESET}  — 50 вопросов начиная с N (или до конца, если осталось меньше)")
    print(f"  {CYAN}0{RESET}  — Выход\n")

    while True:
        choice = input("Ваш выбор: ").strip()
        if choice == "0":
            print("До свидания!")
            sys.exit(0)
        if choice in ("1", "2", "3"):
            return int(choice)
        print(f"{RED}Введите 1, 2, 3 или 0.{RESET}")

def get_range_mode1(total):
    while True:
        try:
            n = int(input(f"Введите N (1 – {total}): ").strip())
            if 1 <= n <= total:
                return 1, n
            print(f"{RED}Число должно быть от 1 до {total}.{RESET}")
        except ValueError:
            print(f"{RED}Введите целое число.{RESET}")

def get_range_mode2(total):
    while True:
        try:
            n = int(input(f"Введите начало диапазона (1 – {total}): ").strip())
            m = int(input(f"Введите конец диапазона ({n} – {total}): ").strip())
            if 1 <= n <= m <= total:
                return n, m
            print(f"{RED}Убедитесь: 1 ≤ начало ≤ конец ≤ {total}.{RESET}")
        except ValueError:
            print(f"{RED}Введите целые числа.{RESET}")

def get_range_mode3(total):
    min_start = 1
    max_start = total  # even if only 1 question left it's fine
    while True:
        try:
            n = int(input(f"Введите начальный номер вопроса (1 – {total}): ").strip())
            if min_start <= n <= max_start:
                end = min(n + 49, total)  # up to 50 questions
                return n, end
            print(f"{RED}Число должно быть от {min_start} до {max_start}.{RESET}")
        except ValueError:
            print(f"{RED}Введите целое число.{RESET}")

def ask_question(q, index, total):
    """Display question, collect answer, return (is_correct, user_answers, correct_answers)."""
    print(f"\n{BOLD}Вопрос {index}/{total}  [№{q['id']}]{RESET}")
    print(f"{q['question']}\n")

    letters = [a["id"] for a in q["answers"]]
    for a in q["answers"]:
        print(f"  {CYAN}{a['id']}{RESET})  {a['text']}")

    correct_ids = get_correct_ids(q)
    multi = len(correct_ids) > 1

    if multi:
        print(f"\n{YELLOW}(Несколько правильных ответов — введите буквы через пробел или запятую){RESET}")

    while True:
        raw = input("\nВаш ответ: ").strip().lower()
        # split by space or comma
        user_ids = [x.strip() for x in raw.replace(",", " ").split() if x.strip()]
        user_ids = list(dict.fromkeys(user_ids))  # deduplicate, preserve order

        if not user_ids:
            print(f"{RED}Пожалуйста, введите хотя бы один вариант ответа.{RESET}")
            continue

        invalid = [x for x in user_ids if x not in letters]
        if invalid:
            print(f"{RED}Неизвестные варианты: {', '.join(invalid)}. Доступны: {', '.join(letters)}{RESET}")
            continue
        break

    is_correct = sorted(user_ids) == sorted(correct_ids)

    if is_correct:
        print(f"\n{GREEN}{BOLD}✓ Верно!{RESET}")
    else:
        user_texts = [a["text"] for a in q["answers"] if a["id"] in user_ids]
        correct_texts = get_correct_texts(q)
        print(f"\n{RED}{BOLD}✗ Неверно.{RESET}")
        print(f"  Вы ответили:  {RED}{'; '.join(user_texts)}{RESET}")
        print(f"  Правильно:    {GREEN}{'; '.join(correct_texts)}{RESET}")

    input(f"\n{YELLOW}[Enter] — следующий вопрос{RESET}")
    return is_correct, user_ids, correct_ids

def run_session(questions_subset):
    """Run a quiz session and return stats."""
    total = len(questions_subset)
    wrong_questions = []

    for i, q in enumerate(questions_subset, 1):
        clear()
        print_header()
        is_correct, user_ids, correct_ids = ask_question(q, i, total)
        if not is_correct:
            wrong_questions.append({
                "question": q,
                "user_ids": user_ids,
                "correct_ids": correct_ids
            })

    return wrong_questions

def show_summary(wrong_questions, total):
    clear()
    print_header()
    correct_count = total - len(wrong_questions)
    pct = correct_count / total * 100

    print(f"{BOLD}═══════════════════ РЕЗУЛЬТАТЫ ═══════════════════{RESET}\n")
    print(f"  Всего вопросов:   {total}")
    print(f"  {GREEN}Правильно:        {correct_count}{RESET}")
    print(f"  {RED}Неправильно:      {len(wrong_questions)}{RESET}")
    print(f"  Результат:        {BOLD}{pct:.1f}%{RESET}\n")

    if pct >= 90:
        grade = f"{GREEN}Отлично!{RESET}"
    elif pct >= 75:
        grade = f"{YELLOW}Хорошо{RESET}"
    elif pct >= 60:
        grade = f"{YELLOW}Удовлетворительно{RESET}"
    else:
        grade = f"{RED}Нужно больше практики{RESET}"

    print(f"  Оценка:           {grade}\n")

    if wrong_questions:
        print(f"{BOLD}{RED}══════════ РАЗБОР ОШИБОК ══════════{RESET}\n")
        for i, entry in enumerate(wrong_questions, 1):
            q = entry["question"]
            user_texts  = [a["text"] for a in q["answers"] if a["id"] in entry["user_ids"]]
            correct_texts = get_correct_texts(q)

            print(f"{BOLD}{i}. [№{q['id']}] {q['question']}{RESET}")
            print(f"   {RED}Ваш ответ:   {'; '.join(user_texts)}{RESET}")
            print(f"   {GREEN}Правильно:   {'; '.join(correct_texts)}{RESET}\n")
    else:
        print(f"{GREEN}{BOLD}Отличная работа — ни одной ошибки!{RESET}\n")

def main():
    clear()
    print_header()

    try:
        all_questions = load_questions()
    except FileNotFoundError:
        print(f"{RED}Файл questions.json не найден. Убедитесь, что он находится в той же папке.{RESET}")
        sys.exit(1)

    total = len(all_questions)
    print(f"  Загружено вопросов: {BOLD}{total}{RESET}\n")

    mode = choose_mode(total)

    if mode == 1:
        start, end = get_range_mode1(total)
    elif mode == 2:
        start, end = get_range_mode2(total)
    else:  # mode == 3
        start, end = get_range_mode3(total)

    # Select questions by their 1-based id (questions are in order 1..300)
    subset = [q for q in all_questions if start <= q["id"] <= end]
    random.shuffle(subset)

    count = len(subset)
    print(f"\n{CYAN}Будет задано {count} вопросов (с {start} по {end}) в случайном порядке.{RESET}")
    input(f"{YELLOW}Нажмите [Enter] для начала...{RESET}")

    wrong = run_session(subset)
    show_summary(wrong, count)

    while True:
        again = input(f"\n{YELLOW}Попробовать ещё раз? (д/н): {RESET}").strip().lower()
        if again in ("д", "y", "да", "yes"):
            main()
        elif again in ("н", "n", "нет", "no"):
            print("До свидания!")
            break

if __name__ == "__main__":
    main()
