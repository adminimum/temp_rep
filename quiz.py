#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import random
import os
import sys

# ── Цвета для терминала ───────────────────────────────────────────────────────
class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    GREEN  = "\033[92m"
    RED    = "\033[91m"
    YELLOW = "\033[93m"
    CYAN   = "\033[96m"
    BLUE   = "\033[94m"
    MAGENTA= "\033[95m"
    WHITE  = "\033[97m"
    DIM    = "\033[2m"

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def header():
    print(f"{C.CYAN}{C.BOLD}")
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║       ПМ03 — Доврачебная медицинская помощь                 ║")
    print("║              Тренажёр тестовых заданий                      ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print(C.RESET)

def load_questions(path="questions.json"):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, path)
    with open(full_path, encoding="utf-8") as f:
        return json.load(f)

def get_int(prompt, lo, hi):
    """Считывает целое число в диапазоне [lo, hi]."""
    while True:
        try:
            val = int(input(prompt))
            if lo <= val <= hi:
                return val
            print(f"{C.RED}  ⚠  Введите число от {lo} до {hi}.{C.RESET}")
        except ValueError:
            print(f"{C.RED}  ⚠  Введите целое число.{C.RESET}")

def show_question(q, num, total):
    """Выводит вопрос и варианты ответов. Возвращает (выбранный_номер, правильный_номер)."""
    print(f"\n{C.BOLD}{C.WHITE}Вопрос {num}/{total}  {C.DIM}[ID {q['id']}]{C.RESET}")
    print(f"{C.YELLOW}{q['question']}{C.RESET}\n")
    opts = q["options"]
    for i, opt in enumerate(opts, 1):
        print(f"  {C.CYAN}{i}{C.RESET}) {opt}")
    print()
    answer = get_int("Ваш ответ: ", 1, len(opts))
    correct = q["answer"]

    if answer == correct:
        print(f"\n{C.GREEN}{C.BOLD}  ✓ Правильно!{C.RESET}")
    else:
        print(f"\n{C.RED}{C.BOLD}  ✗ Неверно.{C.RESET}")
        print(f"  {C.GREEN}Правильный ответ: {correct}) {opts[correct-1]}{C.RESET}")
    input(f"\n{C.DIM}  [Enter — следующий вопрос]{C.RESET}")
    return answer, correct

def run_quiz(questions):
    wrong = []   # [(вопрос, выбранный_ответ)]
    for i, q in enumerate(questions, 1):
        clear()
        header()
        chosen, correct = show_question(q, i, len(questions))
        if chosen != correct:
            wrong.append((q, chosen))

    # ── Итоги ────────────────────────────────────────────────────────────────
    clear()
    header()
    total  = len(questions)
    right  = total - len(wrong)
    pct    = right / total * 100

    color = C.GREEN if pct >= 80 else C.YELLOW if pct >= 60 else C.RED
    print(f"{C.BOLD}{'─'*64}{C.RESET}")
    print(f"  {C.BOLD}РЕЗУЛЬТАТ:{C.RESET}  {color}{C.BOLD}{right} / {total}  ({pct:.1f}%){C.RESET}")
    print(f"{'─'*64}")

    if not wrong:
        print(f"\n  {C.GREEN}{C.BOLD}🎉 Отлично! Все ответы верны!{C.RESET}\n")
    else:
        print(f"\n  {C.RED}{C.BOLD}Ошибочные ответы ({len(wrong)}):{C.RESET}\n")
        for idx, (q, chosen) in enumerate(wrong, 1):
            opts = q["options"]
            print(f"  {C.BOLD}{idx}. [ID {q['id']}] {C.YELLOW}{q['question']}{C.RESET}")
            print(f"     {C.RED}Ваш ответ: {chosen}) {opts[chosen-1]}{C.RESET}")
            print(f"     {C.GREEN}Верный:    {q['answer']}) {opts[q['answer']-1]}{C.RESET}\n")

    input(f"{C.DIM}[Enter — вернуться в меню]{C.RESET}")

def main():
    questions = load_questions()
    total_q   = len(questions)

    while True:
        clear()
        header()
        print(f"  Всего вопросов в базе: {C.BOLD}{total_q}{C.RESET}\n")
        print(f"  {C.CYAN}1{C.RESET}) С 1-го по N-й вопрос")
        print(f"  {C.CYAN}2{C.RESET}) С N-го по M-й вопрос (заданный диапазон)")
        print(f"  {C.CYAN}3{C.RESET}) Случайные 50 вопросов из диапазона N–M")
        print(f"  {C.CYAN}0{C.RESET}) Выход\n")

        mode = get_int("Выберите режим: ", 0, 3)
        if mode == 0:
            print(f"\n{C.DIM}До свидания!{C.RESET}\n")
            sys.exit(0)

        # ── Диапазон ─────────────────────────────────────────────────────────
        if mode == 1:
            n = get_int(f"До какого вопроса (1–{total_q}): ", 1, total_q)
            selected = questions[0:n]

        elif mode == 2:
            n = get_int(f"С какого вопроса (1–{total_q}): ", 1, total_q)
            m = get_int(f"По какой вопрос ({n}–{total_q}): ", n, total_q)
            selected = questions[n-1:m]

        elif mode == 3:
            n = get_int(f"Начало диапазона (1–{total_q}): ", 1, total_q)
            m = get_int(f"Конец диапазона ({n}–{total_q}): ", n, total_q)
            pool = questions[n-1:m]
            count = min(50, len(pool))
            selected = random.sample(pool, count)
            print(f"\n{C.DIM}  Выбрано {count} случайных вопросов из {len(pool)}.{C.RESET}")
            input(f"{C.DIM}  [Enter — начать]{C.RESET}")

        if not selected:
            print(f"{C.RED}  Нет вопросов в выбранном диапазоне.{C.RESET}")
            input()
            continue

        # В режимах 1 и 2 перемешиваем порядок
        if mode in (1, 2):
            random.shuffle(selected)

        run_quiz(selected)

if __name__ == "__main__":
    main()
