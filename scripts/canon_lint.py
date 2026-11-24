#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""canon_lint.py — гейт закона дома: бюджет строк и однозначность номеров
(правило 46 «ЗАКОН ДЕРЖИТ ФОРМУ»; правило 40 «НОМЕР — КЛЮЧ»).

Основа: линт свидетеля-коллеги 24.11 (пакет KANON_46-50_svod, файл 03_canon_lint.py).
Дом-версия добавляет легит-шрамы — по образцу legit_open_states.txt у тревог:
известный шрам не прячется, помечается и ждёт слова Хозяина; нелегит-дубль
или перерасход бюджета красит красным (exit 2).

Использование: python3 canon_lint.py AGENTS.md [бюджет=200]
Выход: 0 — чисто (или только легит-шрамы); 2 — нарушение; любое внутреннее
исключение тоже даёт 2 (fail-closed)."""
import re
import sys

# Известные шрамы нумерации (шрам правила 40). Сворачивание — слово Хозяина.
LEGIT_SCARS = {
    23: "шапка «КООСЯКИ-РЕЕСТР» + издание 1 захода 3 «СТАТУС = КЛЕЙМ»",
    24: "шапка «СТИЛЬ-КАНОН ВЕСЬ АККАУНТ» + издание 1 захода 3 «ШРАМ-ПРОТОКОЛ»",
    25: "шапка «ЖИВОЕ ЛИЦО И ЖИВАЯ КАРТА» + издание 1 захода 3 «СЧЁТ = ТРИАНГУЛЯЦИЯ»",
}


def main():
    path = sys.argv[1]
    budget = int(sys.argv[2]) if len(sys.argv) > 2 else 200
    L = open(path, encoding="utf-8").read().split("\n")
    if L and L[-1] == "":
        L.pop()
    defs, resolved = {}, set()
    for i, s in enumerate(L, 1):
        m = re.match(r"^RESOLVE:\s*(\d+)\s*=", s)
        if m:
            resolved.add(int(m.group(1)))
            continue
        for m in re.finditer(r"ПРАВИЛО (\d+) —\s*([^:(\n]{0,40})", s):
            defs.setdefault(int(m.group(1)), []).append((i, m.group(2).strip()))
        m = re.match(r"^(\d{1,2})\.\s+(?:\*\*(.+?)\*\*|(.{0,40}))", s)
        if m:
            defs.setdefault(int(m.group(1)), []).append(
                (i, (m.group(2) or m.group(3) or "").strip()))
    dups = {n: v for n, v in defs.items() if len(v) > 1}
    print(f"файл: {path}")
    print("строк: %d  бюджет: %d  -> %s" % (
        len(L), budget,
        "ПРЕВЫШЕН на %d" % (len(L) - budget) if len(L) > budget else "в бюджете"))
    print("номеров с определениями: %d; с двойными определениями: %d" % (len(defs), len(dups)))
    for n, v in sorted(dups.items()):
        if n in LEGIT_SCARS:
            tag = "[ЛЕГИТ-ШРАМ]"
        elif n in resolved:
            tag = "[RESOLVE]"
        else:
            tag = "[НЕ РАЗРЕШЁН]"
        line = f"  №{n} {tag}: " + " | ".join(f"стр.{i} «{t[:28]}»" for i, t in v)
        if n in LEGIT_SCARS:
            line += f"  ← {LEGIT_SCARS[n]}"
        print(line)
    unknown = {n for n in dups if n not in LEGIT_SCARS and n not in resolved}
    over = len(L) > budget
    print("ИТОГ:", "КРАСНЫЙ (exit 2)" if (over or unknown) else "зелёный (exit 0)")
    return 2 if (over or unknown) else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as e:  # fail-closed
        print("внутренняя ошибка гейта -> красный:", e)
        sys.exit(2)
