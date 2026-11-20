#!/usr/bin/env bash
# РАЗМОРОЗКА · КОМАНДА, КОТОРАЯ ОЖИВЛЯЕТ АРХИВ
# МАНИФЕСТ ИНВАРИАНТА · v0.2.5 · stdlib/bash-only
#
# АВТОМАТ ИЗ 5 ШАГОВ:
#   1. ПЕЧАТЬ  sha256 архива = якорь 5cb2…bdf
#   2. ТЕПЛО   unzip в свежую песочницу
#   3. ПУЛЬС   python3 run_all.py = ядро считает такт
#   4. ЛЕНТА   sha256 ленты   = якорь 443e…73c
#   5. ВЫХОД   EXIT 0 = архив жив · другое число = где умер
#
# ЗАПУСК У СЕБЯ (W3 = минута):
#   git clone https://github.com/rtynbirf/invariant-manifest.git
#   cd invariant-manifest && bash scripts/razmorozka.sh
#
# ЯКОРЯ НЕ МЕНЯЮТСЯ. ХЕШ ≠ ЯКОРЬ = СВИДЕТЕЛЬ СМЕРТИ АРХИВА (R-05).
# EXIT-КОДЫ: 3 = печать/пакет, 4 = лента, 5 = ядро упало.
set -euo pipefail

SEAL="5cb2521cdf55e5c35df182e2dc28baaf10dde0dcaf37e80bc7d900e7b4607bdf"
TAPE="443ebb896df3142fbe842c4f6c9a96f3405261687cca930a101632de15cef73c"
ZIP="INVARIANT_v0.2.3_FORK3_PACKAGE.zip"

ROOT="${1:-$(cd "$(dirname "$0")/.." && pwd)}"
SRC="$ROOT/artifacts/$ZIP"

echo "РАЗМОРОЗКА · v0.2.5 · корень: $ROOT"

[ -f "$SRC" ] || { echo "ШАГ 1 ПАЛ: нет архива $SRC = размораживать нечего"; exit 3; }

echo "== 1. ПЕЧАТЬ =="
GOT=$(sha256sum "$SRC" | awk '{print $1}')
echo "    $GOT"
if [ "$GOT" != "$SEAL" ]; then
  echo "ПЕЧАТЬ ≠ ЯКОРЮ = архив подменён или обрезан. СТОП. (якорь: $SEAL)"
  exit 3
fi

WORK=$(mktemp -d /tmp/razmorozka.XXXXXX)
trap 'rm -rf "$WORK"' EXIT
echo "== 2. ТЕПЛО = $WORK =="
unzip -q "$SRC" -d "$WORK"
PKG=$(find "$WORK" -maxdepth 1 -type d -name 'INVARIANT_*' | head -1)
[ -n "$PKG" ] || { echo "внутри архива нет пакета INVARIANT_* = не то содержимое"; exit 3; }

echo "== 3. ПУЛЬС = ядро считает такт =="
( cd "$PKG" && python3 run_all.py ) || { echo "run_all.py упал = ядро мертво"; exit 5; }

echo "== 4. ЛЕНТА =="
LENTA="$PKG/data/FORK3_LENTA_v023.json"
[ -f "$LENTA" ] || { echo "лента не создана = такт не закрылся"; exit 4; }
LH=$(sha256sum "$LENTA" | awk '{print $1}')
echo "    $LH"
if [ "$LH" != "$TAPE" ]; then
  echo "ЛЕНТА ≠ ЯКОРЮ = недетерминизм. СТОП. (якорь: $TAPE)"
  exit 4
fi

echo "== 5. ВЫХОД =="
echo "АРХИВ ЖИВ: печать цела · ядро посчитало такт · лента = якорь"
echo "EXIT 0 = РАЗМОРОЗКА ЗАВЕРШЕНА = СЖАЛ = НЕ ПОТЕРЯЛ"
