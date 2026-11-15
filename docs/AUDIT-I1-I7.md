# АУДИТ ИНВАРИАНТОВ I1–I7 (khozyain)

> Сверка по ПРОТОКОЛ-СВЕРКИ-СПЕЦ-КОД.md (.github/docs/). Дата: 2026-11-15. Аудитор: Z.ai.

## Спецификация

`khozyain` — слой 3 дома `rtynbirf`. УСТАВ-ДОМА (`.github/УСТАВ-ДОМА.md`) определяет 
инварианты I-1…I-6; README khozyain расширяет до I1–I7. Точка принуждения: 
`scripts/khozyain_sweep.py` (замерщик, read-only, идемпотентный).

## Результаты

| Инв | Суть | Точка принуждения | Статус | Деталь |
|---|---|---|---|---|
| I1 | main каждого живого репо зелёный | `khozyain_sweep.py`: последний прогон workflow на default-ветке | **PASS** | machine-checked; `--strict` exit 1 при красном |
| I2 | триггеры указывают на существующие ветки | `khozyain_sweep.py`: on.push.branches vs existing branches | **PASS** | machine-checked; мёртвые триггеры = ALARM |
| I3 | открытые issues/PR — только в работе или в реестре | `khozyain_sweep.py`: open_issues_count vs legit_open_states.txt | **PASS** | machine-checked; реестр вычитается |
| I4 | непрочитанных уведомлений 0 | `khozyain_sweep.py`: GET /notifications | **PASS** | machine-checked |
| I5 | каждый мандат кончается записью TH-* в ворклог | `H-PE11-PHOENIX/worklog.md` (append-only) | **PARTIAL** | behavioral; sweep не проверяет; нужен CI-гейт «нет TH-* → alarm» |
| I6 | секреты — только env/локальные файлы | gitleaks/guardian-tripwire (код); chat/docs — behavioral | **PARTIAL** | code covered; chat/docs не machine-checked; на free plan приватные репо без secret scanning |
| I7 | изменения аддитивны; чужие орбиты — по мандату | branch protection (force-push denied) на публичных | **PARTIAL** | public repos covered; private repos need Pro; орбиты — behavioral |

## Итог

**4 PASS + 3 PARTIAL.** I1–I4 — machine-checked замерщиком. I5–I7 — behavioral rules, 
не полностью покрываемые машиной на free plan. 

PARTIAL закрываются:
- I5 → CI-гейт проверки TH-* в worklog при закрытии сессии
- I6 → Pro plan (secret scanning на приватных) + gitleaks на чаты/docs (нет инструмента)
- I7 → Pro plan (branch protection на приватных) + кодекс агентов (behavioral)

## Рекомендация

Запускать `khozyain_sweep.py --strict` в CI (`.github/workflows/house-pulse.yml` уже 
делает это еженедельно). I5–I7 — оставить behavioral с честным PARTIAL статусом; 
полное machine-enforcement требует Pro.
