#!/usr/bin/env python3
"""canon_lint.py — гейт закона: бюджет строк и однозначность номеров (правила 46, 47).
Использование: python3 canon_lint.py AGENTS.md [бюджет=200]
Код выхода: 0 — чисто; 2 — нарушение (fail-closed: любое внутреннее исключение тоже даёт 2)."""
import re, sys
def main():
    path = sys.argv[1]; budget = int(sys.argv[2]) if len(sys.argv) > 2 else 200
    L = open(path, encoding="utf-8").read().split("\n")
    if L and L[-1] == "": L.pop()
    defs, resolved = {}, set()
    for i, s in enumerate(L, 1):
        m = re.match(r"^RESOLVE:\s*(\d+)\s*=", s)
        if m: resolved.add(int(m.group(1))); continue
        for m in re.finditer(r"ПРАВИЛО (\d+) —\s*([^:(\n]{0,40})", s):
            defs.setdefault(int(m.group(1)), []).append((i, m.group(2).strip()))
        m = re.match(r"^(\d{1,2})\.\s+(?:\*\*(.+?)\*\*|(.{0,40}))", s)
        if m: defs.setdefault(int(m.group(1)), []).append((i, (m.group(2) or m.group(3) or "").strip()))
    dups = {n: v for n, v in defs.items() if len(v) > 1}
    unresolved = {n: v for n, v in dups.items() if n not in resolved}
    print(f"файл: {path}\nстрок: {len(L)}  бюджет: {budget}  -> {'ПРЕВЫШЕН на %d' % (len(L)-budget) if len(L)>budget else 'в бюджете'}")
    print(f"номеров с определениями: {len(defs)}; с двойными определениями: {len(dups)}; разрешены строкой RESOLVE: {len(dups)-len(unresolved)}")
    for n, v in sorted(dups.items()):
        print(f"  №{n} {'[RESOLVE]' if n in resolved else '[НЕ РАЗРЕШЁН]'}: " + " | ".join(f"стр.{i} «{t[:28]}»" for i, t in v))
    own = {}
    for n, v in defs.items():
        for i, _ in v: own.setdefault(i, set()).add(n)
    amb = []
    for i, s in enumerate(L, 1):
        for m in re.finditer(r"правил[а-я]*\s+(\d+(?:\s*[/,–-]\s*\d+)*)", s, re.I):
            for n in map(int, re.findall(r"\d+", m.group(1))):
                if n in dups and n not in own.get(i, set()): amb.append((i, n))
    print(f"ссылок на номера с двойным определением: {len(amb)}")
    for i, n in amb: print(f"  стр.{i}: ссылка на №{n}")
    bad = len(L) > budget or bool(unresolved)
    print("ИТОГ:", "КРАСНЫЙ (exit 2)" if bad else "зелёный (exit 0)")
    return 2 if bad else 0
if __name__ == "__main__":
    try: sys.exit(main())
    except SystemExit: raise
    except Exception as e: print("внутренняя ошибка гейта -> красный:", e); sys.exit(2)
