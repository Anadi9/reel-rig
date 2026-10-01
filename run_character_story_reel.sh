#!/usr/bin/env bash
# "I didn't draw a single line of this guy" — character build story reel (vector character, 4 tries).
# Edit remotion/cfg/character-story.json for lines/pauses; visuals in remotion/src/character-story/.
#   --skip-voice  keep the current voiceover (clone takes vary; check the transcript before shipping)
set -euo pipefail
R="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/remotion"
cd "$R"
if [[ " $* " != *" --skip-voice "* ]]; then
  python3 scripts/build_context_voice.py character-story
  python3 -c "
import json;p=json.load(open('public/character-story/props.json'))
open('src/character-story/timing.ts','w').write('// Generated from public/character-story/props.json by the voice build. Seconds.\nexport const SEG = '+json.dumps(p['segments'],indent=1)+' as const;\nexport const VO_TOTAL = '+str(p['voTotal'])+';\n')"
  ~/reel-rig/openvoice/.venv/bin/python3 ~/reel-rig/avatar/lipsync.py public/character-story/vo.wav src/character-story/lipsync.ts
fi
npx remotion render src/index.ts CharacterStoryReel ../out/character-story-reel.mp4
npx remotion render src/index.ts CharacterStoryReelLight ../out/character-story-reel-light.mp4
