# AI agents v2 — "Your next coworker isn't human"

Combines the three commentary angles: the 49-day timeline + scoreboard (logos get screen time), the
"cute is the strategy" hook (NBC: "It's cute. It's cuddly. And it wants your data."), and the coworker narrative.

- Script + sources: `script.json` · scenes: `src/AgentsV2.tsx` · characters: `src/marks.tsx` · thumbnail: `src/Cover.tsx`
- **Landscape (X):** composition `AgentsV2Landscape` (1920×1080) → `../out/agents-v2-landscape.mp4`. Left panel = captions +
  narrator bust; right = a 1080×1080 window onto the portrait stage's action band (y 520–1600), so both cuts share every scene.
- Rebuild: `../run_agents_v2_reel.sh` (`--skip-voice`, `--cover`) → `../out/agents-v2-reel.mp4`, `../out/agents-v2-cover.png`
- Company logos (xAI, Meta, OpenAI) are mono, from `@lobehub/icons-static-svg` (`src/logos.ts`).
  ⚠ That pack's `meta-text.svg` is the **Llama** wordmark — company names are typeset instead.
- Product marks are the colour characters. The Grok glyph is real; **Jolly and the Dots are illustrations
  drawn from press descriptions**, not official art. Swap in real stills if you want exact likeness.
- **Narrator:** `src/VectorBust.tsx`, a head-to-shoulders **redraw** of the vector character (the real rig is in
  `remotion/src/vector-char/` on the Mac and wasn't reachable from the cloud). Bottom-left, lip-synced from
  `src/lipsync.json` (`avatar/lipsync.py`), nods on stresses, brows on emphasis. To use the real rig on the Mac,
  swap `<VectorBust>` in `Narrator` for `VectorActor` cropped to the bust.
- **Voice:** `scripts/build_voice_knn.py`: Piper → **kNN-VC** (github.com/bshall/knn-vc) using `voice-reference.wav` +
  every shipped `.voice-work/*/cloned.wav` as the character's voice → Whisper base.en (sherpa-onnx) per line → best of N takes.
  Median pitch 111 Hz vs 106 Hz in the real reference (Piper alone ≈ 202 Hz). OpenVoice wasn't reachable from the cloud.
  `scripts/check_transcript.py public/vo.wav` re-prints what Whisper hears per line.
- Piper/kNN pronunciation notes: "Three" → "The three biggest names"; "Muse" alone → "news", say "the Muse app";
  "X AI"/"Elon" garble → "Musk ships"; "card" → "credit card"; "Scoreboard" → "First, the score".
- Cloud session: news sites, Hugging Face and Pexels are blocked, so the headline is typeset as a quote card (outlet + date), not a screenshot.
- Remotion uses the Playwright headless shell (`remotion.config.ts`). On the Mac, delete that line.
