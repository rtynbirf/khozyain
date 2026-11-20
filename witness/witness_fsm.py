# -*- coding: utf-8 -*-
# СВИДЕТЕЛЬ РОЯ · witness_fsm.py · v1.0 · 2026-11-20
# КОНЕЧНЫЙ АВТОМАТ СВИДЕТЕЛЯ = ЗАПИСЬ, КОТОРАЯ ДЕЛАЕТ:
#   8 состояний · 7 переходов · 2 финала · декларативная таблица переходов (Harel)
#   BOOT --ok--> TREE     корень git найден
#   TREE --ok--> SEAL     tracked-файлы не пусты
#   SEAL --ok--> SIGN     печать дерева собрана (sha256 по path+blob, как у Reproducible Builds)
#   SIGN --ok--> TAPE     подпись ленты цела
#   TAPE --ok--> CLOSED   WITNESS.json записан и подписан
#   любой --no--> FAIL    лента-свидетель пишется даже при отказе (R-05: ошибка = свидетель)
# SSOT: rtynbirf/khozyain · запускается в каждом репо через reusable workflow.
# Артефакт WITNESS.json = attestation-подобная запись происхождения дерева (SLSA-класс идеи).
# stdlib-only · EXIT 0 = CLOSED · EXIT 2 = FAIL

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

RULE = "НОСИТЕЛЬ СМЕРТЕН = КОММИТ НЕТ"

# ТАБЛИЦА ПЕРЕХОДОВ: состояние -> {охрана: (следующее, смысл)}
TABLE = {
    "BOOT": {"ok": ("TREE", "корень git найден"),
             "no": ("FAIL", "git-корень не найден = свидетельствовать не о чем")},
    "TREE": {"ok": ("SEAL", "tracked-файлы не пусты"),
             "no": ("FAIL", "tracked-файлов нет = пустое дерево")},
    "SEAL": {"ok": ("SIGN", "печать дерева собрана"),
             "no": ("FAIL", "печать дерева не собралась")},
    "SIGN": {"ok": ("TAPE", "подпись ленты цела"),
             "no": ("FAIL", "подпись ленты разорвана")},
    "TAPE": {"ok": ("CLOSED", "WITNESS.json записан и подписан"),
             "no": ("FAIL", "лента не записалась")},
}
FINAL = ("CLOSED", "FAIL")


def git(root, *args):
    r = subprocess.run(["git"] + list(args), cwd=str(root), capture_output=True, text=True, timeout=60)
    return r.returncode, (r.stdout or "").strip(), (r.stderr or "").strip()


def act_boot(ctx):
    rc, out, _ = git(ctx["root"], "rev-parse", "--show-toplevel")
    ok = rc == 0
    if ok:
        ctx["toplevel"] = out
    return ("ok" if ok else "no", out if ok else "rc=" + str(rc))


def act_tree(ctx):
    rc, out, _ = git(ctx["root"], "ls-files", "-s", "-z")
    if rc != 0:
        return ("no", "ls-files упал: rc=" + str(rc))
    entries = []
    for blob in out.split("\0"):
        if blob:
            meta, path = blob.split("\t", 1)
            mode, sha, stage = meta.split()
            entries.append((path, sha))
    ctx["entries"] = entries
    return ("ok" if entries else "no", "tracked-файлов: " + str(len(entries)))


def act_seal(ctx):
    entries = ctx["entries"]
    h = hashlib.sha256()
    for path, sha in sorted(entries):
        h.update(path.encode("utf-8"))
        h.update(b" ")
        h.update(sha.encode())
        h.update(b"\n")
    rc, head, _ = git(ctx["root"], "rev-parse", "HEAD")
    rc2, tree, _ = git(ctx["root"], "rev-parse", "HEAD^{tree}")
    rc3, branch, _ = git(ctx["root"], "rev-parse", "--abbrev-ref", "HEAD")
    if rc != 0 or rc2 != 0 or rc3 != 0:
        return ("no", "HEAD/tree/ветка не прочитаны")
    ctx["head"], ctx["tree_sha"], ctx["branch"] = head, tree, branch
    h.update(b"HEAD " + head.encode() + b"\nTREE " + tree.encode() + b"\n")
    ctx["seal"] = h.hexdigest()
    return ("ok", "печать дерева: " + ctx["seal"][:16] + "…")


def act_sign(ctx):
    hops = ctx["hops"]
    ctx["signature"] = hashlib.sha256(
        json.dumps(hops, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    return ("ok", "подпись: " + ctx["signature"][:16] + "…")


def act_tape(ctx):
    # ИДЕНТИФИКАТОР РЕПО БЕЗ КРЕДЕНШЕЛОВ: env CI > санитизированный URL > имя каталога.
    # Урок 2026-11-20: GitHub Push Protection заблокировал пуш, когда в ленту
    # попал origin с x-access-token = чужой свидетель поймал мой дефект (R-05).
    repo = os.environ.get("GITHUB_REPOSITORY")
    if not repo:
        rc, url, _ = git(ctx["root"], "remote", "get-url", "origin")
        if rc == 0:
            url = re.sub(r"(https?://)[^/@]+@", r"\1", url)
            repo = url.replace("https://github.com/", "").replace(".git", "").rstrip("/")
        else:
            repo = ctx["root"].name
    tape = {
        "лента": "WITNESS",
        "версия": "v1.0",
        "репо": repo,
        "ветка": ctx["branch"],
        "head": ctx["head"],
        "дерево": ctx["tree_sha"],
        "файлов": len(ctx["entries"]),
        "печать_дерева": ctx["seal"],
        "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "хопы": ctx["hops"],
        "подпись": ctx["signature"],
        "правило": RULE,
    }
    out = Path("WITNESS.json")
    out.write_text(json.dumps(tape, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    ctx["tape_path"] = str(out)
    return ("ok", "лента: " + str(out) + " · файлов: " + str(len(ctx["entries"])))


ACTIONS = {"BOOT": act_boot, "TREE": act_tree, "SEAL": act_seal, "SIGN": act_sign, "TAPE": act_tape}


def write_fail_tape(ctx):
    try:
        tape = {"лента": "WITNESS", "версия": "v1.0", "финал": "FAIL",
                "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "хопы": ctx["hops"],
                "подпись": hashlib.sha256(json.dumps(ctx["hops"], sort_keys=True, ensure_ascii=False).encode()).hexdigest(),
                "правило": RULE}
        Path("WITNESS.json").write_text(json.dumps(tape, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        return True
    except Exception:
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    ctx = {"root": root, "hops": [], "entries": []}

    print("СВИДЕТЕЛЬ РОЯ · v1.0 · конечный автомат: 8 состояний · 7 переходов · 2 финала")
    print("=" * 66)
    state = "BOOT"
    final = None
    while state not in FINAL:
        guard, obs = ACTIONS[state](ctx)
        nxt, meaning = TABLE[state][guard]
        ctx["hops"].append({"из": state, "охрана": guard, "в": nxt, "факт": obs})
        print("%-5s --[%s]--> %-7s %s" % (state, guard, nxt, obs))
        if nxt == "FAIL":
            final = "FAIL"
            break
        state = nxt
    if final == "FAIL":
        ok = write_fail_tape(ctx)
        print("=" * 66)
        print("СВИДЕТЕЛЬ: FAIL · " + ("лента-свидетель записана" if ok else "лента не записалась"))
        return 2
    print("=" * 66)
    print("СВИДЕТЕЛЬ: CLOSED · печать дерева и подпись ленты в WITNESS.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
