#!/usr/bin/env bash
# "AI just hacked 395 organizations" (PaperCut) AI News reel: article screenshots -> Piper -> OpenVoice clone
# -> timing + lip-sync -> Remotion render. Edit remotion/cfg/papercut.json for lines/pauses.
#   --skip-voice  keep the current voiceover (clone takes vary; check the transcript before shipping)
#   --reshoot     re-capture the article screenshots (scripts/capture_articles.mjs)
set -euo pipefail
R="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/remotion"
cd "$R"
if [[ " $* " == *" --reshoot "* ]]; then
  node scripts/capture_articles.mjs
  python3 -c "
import json;d=json.load(open('public/papercut/shots/shots.json'))
d={k:{'w':v['w'],'h':v['h'],'url':v['url'],'lines':v['lines']} for k,v in d.items()}
open('src/papercut/shots.ts','w').write('// Generated from public/papercut/shots/shots.json (scripts/capture_articles.mjs). Image px, DPR 2.\nconst SHOTS = '+json.dumps(d,indent=1)+' as const;\nexport default SHOTS;\n')"
fi
if [[ " $* " != *" --skip-voice "* ]]; then
  python3 scripts/build_context_voice.py papercut
  python3 -c "
import json;p=json.load(open('public/papercut/props.json'))
open('src/papercut/timing.ts','w').write('// Generated from public/papercut/props.json by the voice build. Seconds.\nexport const SEG = '+json.dumps(p['segments'],indent=1)+' as const;\nexport const VO_TOTAL = '+str(p['voTotal'])+';\n')"
  ~/reel-rig/openvoice/.venv/bin/python3 ~/reel-rig/avatar/lipsync.py public/papercut/vo.wav src/papercut/lipsync.ts
fi
npx remotion render src/index.ts PapercutReel ../out/papercut-reel.mp4
