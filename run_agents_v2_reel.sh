#!/usr/bin/env bash
# "Your next coworker isn't human" — AI agents v2 (Grok Bot / Muse / Dots). Self-contained Remotion project in agents-v2/.
# Edit agents-v2/script.json (say = Piper text, show = captions, ' / ' = caption break), then run this.
#   --skip-voice  keep the current public/vo.wav + src/timing.json
#   --cover       also render the light thumbnail (out/agents-v2-cover.png)
set -euo pipefail
D="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/agents-v2"
cd "$D"
[[ -d node_modules ]] || npm i
if [[ " $* " != *" --skip-voice "* ]]; then LEN_SCALE=0.9 python3 scripts/build_voice.py; fi
npx remotion render src/index.tsx AgentsV2 ../out/agents-v2-reel.mp4
if [[ " $* " == *" --cover "* ]]; then npx remotion still src/index.tsx AgentsV2Cover ../out/agents-v2-cover.png; fi
