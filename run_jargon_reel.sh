#!/usr/bin/env bash
# "Everyone was lying" — JARGON resource-drop reel (vector skit + pop quiz).
# Edit remotion/cfg/jargon.json for lines/pauses; visuals in remotion/src/jargon/.
#   --skip-voice  keep the current voiceover (clone takes vary; check the transcript before shipping)
set -euo pipefail
R="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/remotion"
cd "$R"
if [[ " $* " != *" --skip-voice "* ]]; then
  python3 scripts/build_context_voice.py jargon
  python3 -c "
import json;p=json.load(open('public/jargon/props.json'))
open('src/jargon/timing.ts','w').write('// Generated from public/jargon/props.json by the voice build. Seconds.\nexport const SEG = '+json.dumps(p['segments'],indent=1)+' as const;\nexport const VO_TOTAL = '+str(p['voTotal'])+';\n')"
  ~/reel-rig/openvoice/.venv/bin/python3 ~/reel-rig/avatar/lipsync.py public/jargon/vo.wav src/jargon/lipsync.ts
fi
npx remotion render src/index.ts JargonReel ../out/jargon-reel.mp4
