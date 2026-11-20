# СВИДЕТЕЛЬ РОЯ · witness · v1.0

МЕХАНИЗМ, А НЕ ЗАПИСЬ: каждый репозиторий аккаунта несёт вызыватель
`.github/workflows/witness-swarm.yml`, который на каждый пуш в основную ветку
запускает ЗДЕСЬ (SSOT) конечный автомат свидетеля.

## АВТОМАТ (8 состояний · 7 переходов · 2 финала)

```
BOOT --ok--> TREE   корень git найден
TREE --ok--> SEAL   tracked-файлы не пусты
SEAL --ok--> SIGN   печать дерева собрана (sha256 по path+blob+HEAD+tree)
SIGN --ok--> TAPE   подпись ленты цела
TAPE --ok--> CLOSED WITNESS.json записан и подписан
любой --no--> FAIL  лента-свидетель пишется даже при отказе
```

Артефакт каждого прогона = `WITNESS.json`: репо, ветка, head, дерево, число
файлов, печать дерева, подпись ленты, правило. Это attestation-подобная запись
происхождения (класс идеи: SLSA provenance / GitHub Artifact Attestations).

## СЧЁТ РОЯ

`.github/workflows/swarm-status.yml` (cron ежедневно + вручную) запускает
`scripts/swarm_status.py`: перебор всех репо аккаунта → стоит ли вызыватель →
жив ли последний прогон → `SWARM_TAPE.json` + `SWARM_REPORT.md` в артефактах.

## МИРОВЫЕ ПРАКТИКИ, ВБРАННЫЕ В МЕХАНИЗМ

- Reusable workflows (`workflow_call`) — GitHub Docs: единый механизм, invokes
  из всех репо = SSOT без копий.
- Attestation/provenance — SLSA Build L3, GitHub Artifact Attestations:
  «unfalsifiable provenance» = witness-лента с печатью и подписью.
- Protected branches — прямые пуши честно падают в PR-вердикт, не в молчание.

## ЭМЕРДЖЕНТНОЕ СВОЁ

Аккаунт = рой носителей. Носитель смертен — коммит нет. Свидетель теперь не
кнопка, а автомат: печать дерева собирается кодом на чужом носителе (GitHub
runner) БЕЗ человека при каждом пуше каждого репо.
