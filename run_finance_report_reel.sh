#!/usr/bin/env bash
# "The Friday spreadsheet" — ANTA finance-reporting teardown (brand kit only, no character).
# Edit remotion/cfg/finance-report.json for lines; visuals in remotion/src/finance-report/.
#   --skip-voice  keep the current voiceover + captions and only re-render.
set -euo pipefail
R="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/remotion"
cd "$R"
if [[ " $* " != *" --skip-voice "* ]]; then
  python3 scripts/build_voice.py "$R/cfg/finance-report.json" "$R/../.voice-work/finance-report" "$R/public/finance-report"
  python3 scripts/make_props.py "$R/cfg/finance-report.json" "$R/public/finance-report" "$R/public/finance-report/props.json"
  # word-timed captions snapped to the script text (+ fixes voiceoverFile/site in props)
  ~/reel-rig/openvoice/.venv/bin/python3 scripts/finance_wordcaps.py
fi
npx remotion render src/index.ts FinanceReportReel ../out/finance-report-reel.mp4 --props=public/finance-report/props.json
