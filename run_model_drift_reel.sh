#!/usr/bin/env bash
# "The AI did" (model drift) Builder Wisdom reel: Piper -> OpenVoice clone -> timing + lip-sync -> Remotion render.
# Edit remotion/cfg/model-drift.json to change lines/pauses; captions, poses and scenes re-time themselves.
# Poses per line: SCRIPT in remotion/src/model-drift/ModelDriftReel.tsx.
set -euo pipefail
R="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/remotion"
cd "$R"
if [[ "${1:-}" != "--skip-voice" ]]; then
  python3 scripts/build_context_voice.py model-drift
  python3 -c "
import json;p=json.load(open('public/model-drift/props.json'))
open('src/model-drift/timing.ts','w').write('// Generated from public/model-drift/props.json by the voice build. Seconds.\nexport const SEG = '+json.dumps(p['segments'],indent=1)+' as const;\nexport const VO_TOTAL = '+str(p['voTotal'])+';\n')"
  ~/reel-rig/openvoice/.venv/bin/python3 ~/reel-rig/avatar/lipsync.py public/model-drift/vo.wav src/model-drift/lipsync.ts
fi
npx remotion render src/index.ts ModelDriftReel ../out/model-drift-reel.mp4
