#!/usr/bin/env python3
"""ХОЗЯИН ДОМА · замерщик состояния аккаунта (read-only, идемпотентный).

Проверяет инварианты I1–I4 (README):
  I1 красные main: последний прогон каждого workflow на default-ветке
  I2 мёртвые триггеры: значения on.push.branches указывают на существующие ветки
  I3 открытые состояния: issues/PR вне реестра legit_open_states.txt
  I4 непрочитанные уведомления

Выход: таблица на stdout + маркеры ALARM; --strict → exit 1 при тревогах.
Токен — только env GH_TOKEN. Секреты в вывод не попадают.
"""
import base64, json, os, re, sys, urllib.request, urllib.error
from urllib.parse import quote as _q

API = "https://api.github.com"
HDR = {"Authorization": f"token {os.environ['GH_TOKEN']}",
       "Accept": "application/vnd.github+json", "User-Agent": "khozyain-sweep"}


def req(path, _tries=3):
    import http.client, time
    r = urllib.request.Request(API + path)
    for k, v in HDR.items():
        r.add_header(k, v)
    last = None
    for i in range(_tries):
        try:
            with urllib.request.urlopen(r, timeout=40) as resp:
                return resp.status, json.loads(resp.read() or b"{}")
        except urllib.error.HTTPError as e:
            try:
                return e.code, json.loads(e.read() or b"{}")
            except Exception:
                return e.code, {}
        except (urllib.error.URLError, http.client.RemoteDisconnected, TimeoutError, ConnectionError, OSError) as e:
            last = e
            time.sleep(2 * (i + 1))  # транзиент сети — ретрай, не падение
    return 0, {"message": f"сеть: {last}"}


def legit_states():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "legit_open_states.txt")
    out = set()
    if os.path.isfile(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#"):
                out.add(line.split("|")[0].strip())
    return out


def main():
    strict = "--strict" in sys.argv
    legit = {s.split("/")[-1] for s in legit_states()}  # реестр хранит короткие имена
    alarms, notes = [], []

    st, repos = req("/user/repos?per_page=100&affiliation=owner,collaborator")
    own = [r for r in repos if not r["fork"] and not r["archived"]] if isinstance(repos, list) else []
    print(f"ДОМ: {len(own)} живых репо (без fork/архив)")

    for r in own:
        full = r["full_name"]; db = r["default_branch"]
        short = full.split("/")[-1]
        st, iss = req(f"/repos/{full}/issues?state=open&per_page=100")
        if st == 200:
            real = [i for i in iss if "pull_request" not in i]
            if real and short not in legit:
                alarms.append(f"I3 OPEN_STATE {full}: issues {len(real)}")
        st, prs = req(f"/repos/{full}/pulls?state=open&per_page=50")
        if st == 200 and prs and short not in legit:
            alarms.append(f"I3 OPEN_STATE {full}: PR {len(prs)}")

        st, wfs = req(f"/repos/{full}/actions/workflows?per_page=100")
        for wf in (wfs.get("workflows", []) if st == 200 else []):
            wid, wname = wf["id"], wf["name"]
            st, runs = req(f"/repos/{full}/actions/workflows/{wid}/runs?per_page=1")
            runs = runs.get("workflow_runs", []) if st == 200 else []
            if runs and runs[0]["head_branch"] == db and runs[0]["conclusion"] == "failure" and short not in legit:
                alarms.append(f"I1 RED_MAIN {full} [{wname}] run {runs[0]['id']}")

        st, files = req(f"/repos/{full}/contents/.github/workflows")
        st2, branches = req(f"/repos/{full}/branches?per_page=100")
        names = {b["name"] for b in branches} if st2 == 200 and isinstance(branches, list) else set()
        for f in (files if st == 200 and isinstance(files, list) else []):
            if not f["name"].endswith((".yml", ".yaml")):
                continue
            stc, fc = req(f"/repos/{full}/contents/.github/workflows/{_q(f['name'])}")
            if stc != 200:
                continue
            raw = base64.b64decode(fc.get("content", ""))
            in_push = False
            for line in raw.decode("utf-8", "replace").splitlines():
                s = line.strip()
                if re.match(r"^(push|pull_request):\s*$", s):
                    in_push = True; continue
                if s and not line.startswith(" "):
                    in_push = False
                m = re.match(r"^branches:\s*(.+)$", s) if in_push else None
                if m:
                    val = m.group(1).strip()
                    if val.startswith("["):
                        if "]" in val:
                            val = val[:val.index("]") + 1]   # отрезать inline-комментарий после ]
                        vals = [v.strip().strip("'\"") for v in val.strip("[]").split(",")]
                    else:
                        vals = [re.split(r"\s+#", val)[0].strip("'\"")]
                    for v in vals:
                        if v and "*" not in v and v not in names:
                            alarms.append(f"I2 DEAD_TRIGGER {full} [{f['name']}] ветка '{v}' не существует")

    st, notif = req("/notifications?per_page=100")
    unread = [n for n in notif if isinstance(n, dict) and n.get("unread")] if st == 200 and isinstance(notif, list) else []
    if unread:
        alarms.append(f"I4 UNREAD_NOTIFICATION: {len(unread)}")
    notes.append(f"непрочитанных уведомлений: {len(unread)}")

    print("\n".join(notes))
    if alarms:
        print(f"\n=== ТРЕВОГИ ({len(alarms)}) ===")
        print("\n".join("  " + a for a in alarms))
    else:
        print("\n=== ДОМ ЧИСТ: инварианты I1–I4 держатся ===")
    sys.exit(1 if (strict and alarms) else 0)


if __name__ == "__main__":
    main()
