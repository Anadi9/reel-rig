#!/usr/bin/env bash
# "Guess what it costs" — STACK resource-drop reel (countdown + $0 reveal).
# Edit remotion/cfg/stack.json for lines/pauses; visuals in remotion/src/stack/.
#   --skip-voice  keep the current voiceover. USE THIS unless you changed a line: the shipped vo.wav is take 3
#                 with take 1's Claude lines spliced in (.voice-work/stack/takes); a rebuild gives a fresh random take.
set -euo pipefail
R="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/remotion"
cd "$R"
if [[ " $* " != *" --skip-voice "* ]]; then
  python3 scripts/build_context_voice.py stack
  python3 -c "
import json;p=json.load(open('public/stack/props.json'))
open('src/stack/timing.ts','w').write('// Generated from public/stack/props.json by the voice build. Seconds.\nexport const SEG = '+json.dumps(p['segments'],indent=1)+' as const;\nexport const VO_TOTAL = '+str(p['voTotal'])+';\n')"
  ~/reel-rig/openvoice/.venv/bin/python3 ~/reel-rig/avatar/lipsync.py public/stack/vo.wav src/stack/lipsync.ts
fi
npx remotion render src/index.ts StackReel ../out/stack-reel.mp4
