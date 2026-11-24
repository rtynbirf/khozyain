# MIR2 · вторая сверка КАНОН × МИР · запись ночи 2026-11-24 (~01:36 UTC)

Режим: **дом без ключа** (ключ из переписки мёртв — 401 на пробе ~01:30 UTC;
последний живой акт ключа ~01:13 UTC, раунд клеток). Проверка шла публичными
каналами: HTML github.com (свежие), raw.githubusercontent.com/HEAD (свежие),
api.github.com анонимно — бюджет IP исчерпан (0/60), api через веб-ридер —
**устаревший CDN** (био «69 репо · 3800+», pushed_at 22.11 — отброшено как лежь
кэша, помечено, не использовано). Клоны восьми репо (git, HEAD).

## Найдено (с метками канала)

- БИО (HTML, живое): «Полимат-универсум: автономные агенты · генеративное медиа ·
  офлайн-суверенитет. Живой счёт роя — SWARM-SYNC в README профиля. Витрина:
  rtynbirf.github.io» — байт-в-байт = PHASE3.bio_after. 81 репо. Ручных чисел нет.
- README профиля (raw/HEAD): сентинели BEGIN/END_SWARM_SYNC = 1/1, один блок,
  штамп «2026-11-23 23:49 UTC», источник объявлен в блоке, 81 репо · 12311
  коммитов · последний push 23.11 · топ-5: rtynbirf 618, .github 502, markitdown
  502, cell-swarm 488, H-PE11-PHOENIX 403. «0 приватных» сходится с двумя
  каналами прошлой ночи (PHASE1: public 81 = owner 81); polymat-hive публичен
  (клон без ключа; первая попытка 401 — опечатка polimat/polymat, моя, записана).
- Органы после смерти ключа (HTML Actions, 24.11 после 00:38 UTC): protocol-verify
  #48 ✓, летопись-страж #46 ✓, dom-avtomat #39 ✓, СТРАЖ КРАСНЫХ #1 ✓ (ручной),
  Dependabot #63 ✓, Доктор гейтов — skipped. Красных нет. Дом не держится за
  смертный носитель.
- ПУЛЬС v2 = polymath-os/.github/workflows/self-audit.yml (имя «ПУЛЬС v2 —
  еженедельный самоаудит», cron 17 4 * * 1, GITHUB_TOKEN + PULSE_SIGNING_KEY).
  #13 красный (админ-PAT) → #15 зелёный (GITHUB_TOKEN). Следующий scheduled:
  понедельник 30.11 04:17 UTC.
- СТРАЖ КРАСНЫХ = red-sentinel.yml, cron 31 5 * * * (ежедневно 05:31 UTC);
  сегодняшний прогон — первый полный обход после смерти ключа.
- SVG (STATIC, клоны): rtynbirf 45/45 без `<title>`; rtynbirf.github.io 3/3;
  прочие репо — тоже без дубля (singulyar 3, lex-naturae 2, polymath-os 3,
  repo-doctrine 3, karta 2, polymat-hive 3).
- Долгоживущие секреты в ссылках воркфлоу (STATIC): REVO_PAT (revomat-central,
  rtynbirf, */15), W3_PAT (repo-doctrine: pin-drift-watch, wave3-door-lint
  [отключён], wave3-dpr-grader), KARTA_TOKEN (karta-nightly, 03:21),
  CELL_SWARM_DISPATCH_TOKEN (blood), HIVE_ALARM_TOKEN (hive-alarm, 05:40),
  LIVING_SHIELD_TOKEN (living-shield, воскресенье), COPILOT_PAT (polymat-hive).
  Не руки: PULSE_SIGNING_KEY, SOPS_AGE_KEY (подпись/шифрование).
- Канон (клон rtynbirf/AGENTS.md, 202 строки): правила 1–42; 38–42 заняты
  (клетки/22.11); правило 40 НОМЕР—КЛЮЧ → патчи свидетеля перенумерованы 43–45.
  Дубли 23–27 — известный шрам (записан в правиле 40).

## Не проверено этим каналом (требует ключа) — помечено, не выдумано

- ruleset 26757855: байпас-лист (публично не читается).
- Значения/состав секретов Actions (админ-ручка).
- Полный пересчёт коммитов 81 репо (счёт блока 12311 зафиксирован, не перепроверен).
- Логи двух красных расписаний 23.11 в repo-doctrine (agentic-pilot, wf-lint).
- Один ручной SWARM-SYNC прогон висит Queued с вечера (~2 ч) — кандидат на cancel.
- Живость crons rtynbirf (pulse */30, serdtse-takta, revomat-central */15) — на
  странице видны только прогон-события 23.11; статус disabled/active требует API.

## Ближайшие расписания-пробы (покажут, умер ли какой-то секрет с ключом)

- 03:17 UTC — swarm-sync (обновит штамп блока)
- 03:21 UTC — karta-nightly (KARTA_TOKEN)
- 05:31 UTC — СТРАЖ КРАСНЫХ (первый полный обход после смерти ключа)
- 05:40 UTC — hive-alarm (HIVE_ALARM_TOKEN)

## Артефакты такта

- download/AGENTS_kanon_43-45.md · download/kanon_patch_43-45.diff ·
  download/KANON_PATCH_43-45_README.md (git apply --check — зелёный)
- Мёртвый ключ выметен: work/.gh_token2 удалён (401; ценности нет).
- Незапечатанный остаток: канон-коммит и запись в репо-нить — ждут руки
  (короткий fine-grained PAT или рука человека через веб).

Provenance: ХОЗЯИН-канал, песочница, скрипты scripts/mir2_*.py,
scripts/kanon_patch_43_45_build.py. REVE=РЕВО
