#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""canon_lint.py — гейт закона дома: бюджет строк и однозначность номеров
(правило 46 «ЗАКОН ДЕРЖИТ ФОРМУ»; правило 40 «НОМЕР — КЛЮЧ»).

Основа: линт свидетеля-коллеги 24.11 (пакет KANON_46-50_svod, файл 03_canon_lint.py).
Дом-версия: 24.11.2026 СВЕРНИ свернул дубли 23–25 (слово минтовано ХОЗЯИНОМ дома
по делегации КЛЮЧНИКА) — легит-список ОПУСТОШЁН и должен оставаться пустым:
любой новый дубль номеров = красный (правило 40), разрешений больше нет.
Канарейка (правило 48 «СТРАЖ УМЕЕТ КРАСНЕТЬ»): python3 canon_lint.py --canary —
страж обязан покраснеть на неисправном образце; не покраснел — страж НЕ ПРОВЕРЕН
(правила 39/48) и сам даёт exit 2.

Использование:
  python3 canon_lint.py AGENTS.md [бюджет=200]   — прогон гейта
  python3 canon_lint.py --canary                 — красный прогон стража
Выход: 0 — чисто (или канарейка поймана); 2 — нарушение; любое внутреннее
исключение тоже даёт 2 (fail-closed)."""
import os
import re
import sys
import tempfile

# Легит-шрамы нумерации (шрам правила 40). История: до 24.11.2026 здесь жили
# двойные определения 23–25 (шапка + издание 1 захода 3) и ждали слова Хозяина.
# 24.11.2026 СВЕРНИ свернул их — список ПУСТ; механизм оставлен для честной
# записи будущих шрамов, но каждая запись теперь требует явного слова КЛЮЧНИКА.
LEGIT_SCARS = {}


def check(path, budget, out=print):
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
    out(f"файл: {path}")
    out("строк: %d  бюджет: %d  -> %s" % (
        len(L), budget,
        "ПРЕВЫШЕН на %d" % (len(L) - budget) if len(L) > budget else "в бюджете"))
    out("номеров с определениями: %d; с двойными определениями: %d" % (len(defs), len(dups)))
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
        out(line)
    unknown = {n for n in dups if n not in LEGIT_SCARS and n not in resolved}
    over = len(L) > budget
    out("ИТОГ:", "КРАСНЫЙ (exit 2)" if (over or unknown) else "зелёный (exit 0)")
    return 2 if (over or unknown) else 0


def canary():
    """Красный прогон (правило 48): неисправный образец ОБЯЗАН быть пойман."""
    d = tempfile.mkdtemp(prefix="canon_lint_canary_")
    sample = os.path.join(d, "broken.md")
    body = ["образец неисправного закона"] + ["наполнитель без номеров"] * 205
    body += ["7. ПРАВИЛО СЕМИ.", "7. ДУБЛЬ СЕМИ."]
    open(sample, "w", encoding="utf-8").write("\n".join(body) + "\n")
    code = check(sample, 200, out=lambda *_: None)
    if code == 2:
        print("КАНАРЕЙКА: страж покраснел на неисправном образце "
              "(дубль №7 + перерасход бюджета) — проверка жива, exit 0")
        return 0
    print("КАНАРЕЙКА: страж НЕ покраснел — СТРАЖ НЕ ПРОВЕРЕН (правила 39/48), exit 2")
    return 2


def main():
    if "--canary" in sys.argv:
        return canary()
    return check(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 200)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as e:  # fail-closed
        print("внутренняя ошибка гейта -> красный:", e)
        sys.exit(2)
