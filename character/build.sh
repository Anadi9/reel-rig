#!/usr/bin/env bash
# Rebuild Anadi's full-body pixel character end to end and sync it into Remotion.
#   1. poses      build_character.py  → illustrated/, pixel/ (2px, face-aligned)
#   2. mouths     build_mouths.py     → pixel_mouths/<pose>/<viseme>.png
#   3. review     review_mouths.py    → mouth_board.png   ·  character_sheet.py → character_sheet.png
#   4. sync       → remotion/public/character/{illustrated,pixel,pixel_mouths}
set -euo pipefail
cd "$(dirname "$0")"
PY=~/reel-rig/openvoice/.venv/bin/python3
PUB=../remotion/public/character

$PY build_character.py
$PY build_mouths.py
$PY review_mouths.py
$PY character_sheet.py
mkdir -p "$PUB"
for d in illustrated pixel pixel_mouths; do
  rm -rf "$PUB/$d"
  cp -R "$d" "$PUB/$d"
done
echo "synced → $PUB"
