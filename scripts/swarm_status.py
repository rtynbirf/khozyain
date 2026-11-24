# -*- coding: utf-8 -*-
# СЧЁТ РОЯ · swarm_status.py · v1.0 · 2026-11-20
# Перебор ВСЕХ репо аккаунта: стоит ли вызыватель свидетеля, жив ли последний прогон.
# Работает и локально (файл-токен аргументом), и в CI (env GITHUB_TOKEN).
# Выход: SWARM_TAPE.json + SWARM_REPORT.md (в cwd или download/ в CI = артефакт).

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

API = "https://api.github.com"
OWNER = "rtynbirf"
PATH = ".github/workflows/witness-swarm.yml"


def get_token():
    if os.environ.get("GITHUB_TOKEN"):
        return os.environ["GITHUB_TOKEN"]
    if len(sys.argv) > 1 and Path(sys.argv[1]).is_file():
        return Path(sys.argv[1]).read_text().strip()
    return None


def api(method, url, body=None, token=None):
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "swarm-status"}
    if token:
        headers["Authorization"] = "token " + token
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode() or "{}")
        except Exception:
            return e.code, {}


def all_repos(token):
    repos, page = [], 1
    while True:
        st, chunk = 200, []
        if token:
            st, chunk = api("GET", f"{API}/user/repos?affiliation=owner&visibility=all&per_page=100&page={page}", token=token)
        if st != 200:
            # GITHUB_TOKEN репо-скопирован: /user/repos даёт 403 без user-контекста.
            # Дом публичен — витрина перечисляется тем же токеном (рана #3, 2026-11-24).
            st, chunk = api("GET", f"{API}/users/{OWNER}/repos?type=owner&per_page=100&page={page}", token=token)
        if st != 200:
            raise SystemExit("перечисление репо не прошло: HTTP " + str(st))
        repos += chunk
        if len(chunk) < 100:
            return repos
        page += 1


def status_repo(name, token):
    rep = {"repo": name}
    st, wf = api("GET", f"{API}/repos/{OWNER}/{name}/contents/{PATH}", token=token)
    if st == 404:
        rep["вердикт"] = "NO_WORKFLOW"
        return rep
    if st != 200:
        rep["вердикт"] = "UNREACHABLE:" + str(st)
        return rep
    rep["workflow"] = "есть"
    st2, wlist = api("GET", f"{API}/repos/{OWNER}/{name}/actions/workflows?per_page=100", token=token)
    run_done = False
    if st2 == 403:
        # честный вердикт вместо тихого NO_RUNS: руку не пустили — это видно, а не спрятано
        rep["вердикт"] = "UNREACHABLE:403"
        return rep
    if st2 == 200:
        for w in wlist.get("workflows", []):
            if w.get("path") == PATH:
                st3, runs = api("GET", f"{API}/repos/{OWNER}/{name}/actions/workflows/{w['id']}/runs?per_page=1", token=token)
                rl = runs.get("workflow_runs") or []
                if rl:
                    rep["последний_прогон"] = rl[0].get("status") + "/" + str(rl[0].get("conclusion"))
                    rep["вердикт"] = {"completed/success": "LIVE",
                                      "completed/failure": "FAILING",
                                      "in_progress": "RUNNING"}.get(
                                          rl[0].get("status") + "/" + str(rl[0].get("conclusion")),
                                          "RUNNING" if rl[0].get("status") != "completed" else "FAILING")
                else:
                    rep["вердикт"] = "NO_RUNS"
                run_done = True
                break
    if not run_done:
        rep["вердикт"] = "NO_RUNS"
    return rep


def main():
    token = get_token()
    repos = all_repos(token)
    print("СЧЁТ РОЯ · репо:", len(repos))
    results = []
    for i, r in enumerate(repos, 1):
        if r.get("size", 0) == 0:
            results.append({"repo": r["name"], "вердикт": "EMPTY"})
            continue
        rep = status_repo(r["name"], token)
        results.append(rep)
        print("%3d/%-3d %-36s %s" % (i, len(repos), rep["repo"], rep["вердикт"]))
    counts = {}
    for rep in results:
        k = rep["вердикт"].split(":")[0]
        counts[k] = counts.get(k, 0) + 1
    tape = {"лента": "SWARM_TAPE", "версия": "v1.0",
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "репо_всего": len(repos), "вердикты": counts, "записи": results}
    md = ["# СЧЁТ РОЯ · " + tape["utc"], "",
          "Репо: " + str(len(repos)) + " · " + json.dumps(counts, ensure_ascii=False), "",
          "| Репо | Вердикт | Последний прогон |", "|---|---|---|"]
    for rep in results:
        md.append("| %s | %s | %s |" % (rep["repo"], rep["вердикт"], rep.get("последний_прогон", "—")))
    for fname, content in (("SWARM_TAPE.json", json.dumps(tape, ensure_ascii=False, indent=1) + "\n"),
                           ("SWARM_REPORT.md", "\n".join(md) + "\n")):
        p = Path(fname)
        p.write_text(content, encoding="utf-8")
        print("записано:", p)


if __name__ == "__main__":
    main()
