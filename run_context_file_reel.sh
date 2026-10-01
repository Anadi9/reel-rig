#!/usr/bin/env bash
# "The AI Context File" reel: Piper -> OpenVoice clone -> timing -> Remotion render.
# Edit remotion/cfg/context-file.json to change lines/pauses; everything re-times itself.
# Swap in your own recording: drop it at remotion/public/context-file/vo.wav and run with --skip-voice
# (keep the same line order and roughly the same pauses, or re-time timing.ts).
set -euo pipefail
R="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/remotion"
cd "$R"
if [[ "${1:-}" != "--skip-voice" ]]; then
  python3 scripts/build_context_voice.py
  python3 -c "
import json;p=json.load(open('public/context-file/props.json'))
open('src/context-file/timing.ts','w').write('// Generated from public/context-file/props.json by the voice build. Seconds.\nexport const SEG = '+json.dumps(p['segments'],indent=1)+' as const;\nexport const VO_TOTAL = '+str(p['voTotal'])+';\n')"
fi
npx remotion render src/index.ts ContextFileReel out/context-file-reel.mp4
open out/context-file-reel.mp4 2>/dev/null || true
