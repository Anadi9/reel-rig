#!/usr/bin/env bash
# "Three giants just launched the same thing" AI News reel (Grok Bot / Muse / Dots): article screenshots ->
# Piper -> OpenVoice clone -> timing + lip-sync -> Remotion render. Edit remotion/cfg/agents.json for lines/pauses.
#   --skip-voice  keep the current voiceover (clone takes vary; check the transcript before shipping)
#   --reshoot     re-capture the article screenshots (scripts/capture_agents.mjs)
set -euo pipefail
R="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/remotion"
cd "$R"
if [[ " $* " == *" --reshoot "* ]]; then
  node scripts/capture_agents.mjs
  python3 -c "
import json;d=json.load(open('public/agents/shots/shots.json'))
d={k:{'w':v['w'],'h':v['h'],'url':v['url'],'lines':v['lines']} for k,v in d.items()}
open('src/agents/shots.ts','w').write('// Generated from public/agents/shots/shots.json (scripts/capture_agents.mjs). Image px, DPR 2.\nconst SHOTS = '+json.dumps(d,indent=1)+' as const;\nexport default SHOTS;\n')"
fi
if [[ " $* " != *" --skip-voice "* ]]; then
  python3 scripts/build_context_voice.py agents
  python3 -c "
import json;p=json.load(open('public/agents/props.json'))
open('src/agents/timing.ts','w').write('// Generated from public/agents/props.json by the voice build. Seconds.\nexport const SEG = '+json.dumps(p['segments'],indent=1)+' as const;\nexport const VO_TOTAL = '+str(p['voTotal'])+';\n')"
  ~/reel-rig/openvoice/.venv/bin/python3 ~/reel-rig/avatar/lipsync.py public/agents/vo.wav src/agents/lipsync.ts
fi
npx remotion render src/index.ts AgentsReel ../out/agents-reel.mp4
