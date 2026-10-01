#!/usr/bin/env bash
# Builds the "AI models are down / Wrapper Test" reel end to end:
# Piper -> OpenVoice clone -> caption transcription -> Remotion render.
# Run this from a normal Terminal on this Mac (not through the cloud bridge —
# Piper, the OpenVoice venv, and Remotion's compositor all need to run
# natively here).
set -euo pipefail

REEL_RIG="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REMOTION="$REEL_RIG/remotion"
CFG="$REMOTION/cfg/wrapper-test.json"
WORK="$REEL_RIG/.voice-work/wrapper-test"

echo "== 1/3  Voice: Piper + OpenVoice clone =="
python3 "$REMOTION/scripts/build_voice.py" "$CFG" "$WORK" "$REMOTION/public"

echo
echo "== 2/3  Captions + render props =="
python3 "$REMOTION/scripts/make_props.py" "$CFG" "$REMOTION/public" "$REMOTION/public/render-props.json"

echo
echo "== 3/3  Remotion render =="
cd "$REMOTION"
npx remotion render src/index.ts WrapperTestReel out/wrapper-test-reel.mp4 --props=public/render-props.json

echo
echo "Done: $REMOTION/out/wrapper-test-reel.mp4"
open "$REMOTION/out/wrapper-test-reel.mp4" 2>/dev/null || true
