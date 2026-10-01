#!/usr/bin/env bash
# "Hey, I'm Anadi" intro reel (character v2, all 34 poses): Piper -> OpenVoice clone -> timing + lip-sync -> Remotion render.
# Edit remotion/cfg/intro.json to change lines/pauses; captions, poses and scenes re-time themselves.
# Poses per line: SCRIPT in remotion/src/intro/IntroReel.tsx. The clone varies run to run — check the
# words with transcribe.py and re-run if a name comes out wrong ("Anta" is spelled that way for Piper).
set -euo pipefail
R="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/remotion"
cd "$R"
if [[ "${1:-}" != "--skip-voice" ]]; then
  python3 scripts/build_context_voice.py intro
  python3 -c "
import json;p=json.load(open('public/intro/props.json'))
open('src/intro/timing.ts','w').write('// Generated from public/intro/props.json by the voice build. Seconds.\nexport const SEG = '+json.dumps(p['segments'],indent=1)+' as const;\nexport const VO_TOTAL = '+str(p['voTotal'])+';\n')"
  ~/reel-rig/openvoice/.venv/bin/python3 ~/reel-rig/avatar/lipsync.py public/intro/vo.wav src/intro/lipsync.ts
fi
npx remotion render src/index.ts IntroReel ../out/intro-reel.mp4
