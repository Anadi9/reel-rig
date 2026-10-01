# Reel notes — read me first

Rules we learned the hard way, and where the latest work lives. Last updated 2026-10-01.

## Rules for every reel

- **Instagram safe zones** (1080×1920, measured from a phone preview):
  - The header and its fade blur the top ~270px, so captions start at y ≥ 280.
  - The like/comment/share column covers x > ~950 from about y 1200 down.
  - The username/caption block starts around y 1720.

  Keep anything important inside x 60–940 and y 280–1600.
- **Voice (Piper): write "AI", never "ay eye".** Piper reads "ay eye" as "aye aye", which sounds like "II". Write "OpenAI" as "Open AI". Plain "AI" was checked with Whisper, including after the voice clone.
  - ⚠ `remotion/cfg/context-v2.json` still uses "ay eye" and probably has the same problem. It hasn't been re-rendered yet.
- **Full-body character:** about 25% of screen height (490px), centred left-to-right, with the pill directly below his feet. Details are in `character/README.md`.
- **Handle:** @the.anadi goes on the CTA/follow pill only when needed, not on the hook.
- **Length:** when a content-package script runs longer than planned, ask before trimming.

## Latest work

- **"Your next coworker isn't human" (AI agents v2: Grok Bot / Muse / Dots)** (no Anadi character; product marks are the cast + narrator bust, 62.0s, 2026-10-01):
  - video: `out/agents-v2-reel.mp4` · cover (light, bold hook): `out/agents-v2-cover.png` · project: `agents-v2/` (self-contained Remotion, own README)
  - landscape for X: `out/agents-v2-landscape.mp4` (1920×1080, composition `AgentsV2Landscape`, same scenes in a 1080² window + captions/bust panel left).
  - rebuild: `./run_agents_v2_reel.sh` (`--skip-voice`, `--cover`). Script + sources: `agents-v2/script.json`.
  - beats: NBC headline hook → 49-day counter + timeline (mono logos) → Day 0 Grok Bot (lid closes, tasks tick) → Day 28 Muse/Jolly → keychain charm
    → Day 49 Dots get named → "Why cute?" robot NOPE / friend → chief-of-staff org chart, teams of Dots, Muse for Small Business, #your-team roster
    → scoreboard (Meta LEADING) → "Who wins?" comment CTA.
  - facts: Grok Bot $300 (SuperGrok Heavy) at launch → in $30 SuperGrok by Aug 26. Meta Sep: "best month since 2013" (sources disagree on %: 25/27/36, so no %).
  - narrator: **vector character bust** bottom-left (`agents-v2/src/VectorBust.tsx`, a redraw, the rig wasn't in the cloud), lip-synced; face kept above y 1720.
  - voice: Piper → kNN-VC in the character's voice (ref = voice-reference.wav + all shipped cloned.wav), best of N takes per line by Whisper; 62.0s.
  - ⚠ lobehub `meta-text.svg` renders "Llama", don't use it as the Meta wordmark.

- **"3 giants launched the same thing" (AI agents: Grok Bot / Muse / Dots) AI-news reel** (vector v3 character + real article screenshots, 41.2s, 2026-10-01):
  - video: `out/agents-reel.mp4` · cover: `out/agents-cover.png` · code: `remotion/src/agents/AgentsReel.tsx` · script + sources: `remotion/cfg/agents.json`
  - rebuild: `./run_agents_reel.sh` (`--skip-voice`, `--reshoot` → `remotion/scripts/capture_agents.mjs`, which now falls back to the whole page when the quote isn't inside `<article>`)
  - PaperCut's Shot window/stamps/captions system, with `VectorAnadi` taking `theme` from the chapter (dark/light alternating per company).
  - Facts: Grok Bot (xAI) beta Aug 11 · Meta Muse Sep 8, avatar "Jolly", #1 App Store above ChatGPT · **Dots is OpenAI's** (Sep 29 DevDay), not Meta's.
  - Axios served a Cloudflare bot check to headless Chrome → dropped. NBC's "is named Jolly" line sits next to property ads → dropped.
  - Piper: bare "Grok Bot." → "Grock Butt"; "the Grok Bot" is clean. "It shot to" garbled → "jumped to".

- **"The Friday spreadsheet" (ANTA finance-reporting teardown)** (brand kit only, NO character, 58.2s, 2026-09-30):
  - video: `out/finance-report-reel.mp4` · cover: `out/finance-report-cover.png` · source: ANTA `content/generated/instagram/2026-10-02-finance-reporting-consolidation.md`
  - code: `remotion/src/finance-report/FinanceReportReel.tsx` · script: `remotion/cfg/finance-report.json` · rebuild: `./run_finance_report_reel.sh` (`--skip-voice` to re-render only)
  - UI mocks carry it: stitched tools → report.xlsx, pointer copy-pasting into a sheet, an error cell + "TRUSTED?" stamp + week strip,
    CRM/Billing → PIPELINE → report with flowing packets, "2–3 WEEK BUILD" card, Friday calendar struck out, typed "your stack" comment + reply.
  - scene animations key off caption words (`cueAt`), so re-voicing keeps sync. Captions: `scripts/finance_wordcaps.py` (word timestamps snapped to script text).
  - build_voice.py needs ABSOLUTE work/public paths (it runs voice.py from the skill dir).

- **"Guess what it costs" reel** (vector character, 54.6s, 2026-09-30, v3, posted as **Builder Wisdom**, no comment CTA):
  - video: `out/stack-reel.mp4` · cover: `out/stack-cover.png` · post copy: `out/stack-reel-caption.md`
  - code: `remotion/src/stack/StackReel.tsx` · script: `remotion/cfg/stack.json` · rebuild: `./run_stack_reel.sh --skip-voice`
    (⚠ always `--skip-voice`: the shipped vo.wav is spliced from takes: take 3 + take 1's Claude lines + a separate
    take of the closing line `wis`, all in `.voice-work/stack/takes/`; the v2 CTA version is `shipped_v2_with_cta.wav`).
  - six tools, 6→1: Perplexity+ChatGPT, ChatGPT+Gemini (real GPT-Image sheets), Claude Code, Claude scheduled
    tasks+Make.com, the reel rig, Claude. Honest total **$20/mo** (one Claude Pro plan); n8n dropped (Cloud has no free tier).
  - retention: a **censored receipt** from frame 0 (rows "#6 ? ? ?", prices + TOTAL under black bars), names fill in
    as counted, bars peel on a full-screen lime cut ($0 rows first, Claude Code $20* last, then TOTAL $20/mo).
    Close: "Stop collecting tools. Pick a few, and build." then loops to the hook frame.
  - the STACK PDF still exists (six tools, same theme): `generated/2026-09-21-resource-drop-resource.{html,pdf}`, unused by v3.
  - Piper + clone: "Claude" never comes out clean ("plot"/"clothe"; "Clode" spelling is least bad); "Chat G P T";
    bare "Three" → "free", say "Number three"; "Make dot com". Perplexity varies per take.
  - `Panel` takes an `extra` node for its title bar (the moon + "while you sleep" lives there; it collided with the Make nodes).

- **"Everyone was lying" (JARGON resource drop) reel** (vector character, style #4 hybrid, 47s):
  - video: `out/jargon-reel.mp4` · code: `remotion/src/jargon/JargonReel.tsx` · script: `remotion/cfg/jargon.json`
  - meeting skit (faceless nodding teammates, "?" over every head) → forgetting-chat demo → hard cut to a
    full-screen lime pop quiz (silent 3-2-1 = the 3.0s gap after `q2`) → hand-up reframe → CTA on the real
    decoder PDF (`public/jargon/img/pdf.png`, row 6 highlighted). The last frame is the hook frame so the loop is seamless.
  - rebuild: `./run_jargon_reel.sh` (`--skip-voice` to only re-render).
  - cover: `out/jargon-cover-{room,quiz}.png` (Still `JargonCover`, prop `variant`), inside the 3:4 grid crop.

- **"AI just hacked 395 organizations" (PaperCut AI-news) reel** (character v2 + real article screenshots, 45s):
  - video: `out/papercut-reel.mp4` · code: `remotion/src/papercut/PapercutReel.tsx` · script: `remotion/cfg/papercut.json`
  - new element, the **Shot window**: real screenshots from `remotion/scripts/capture_articles.mjs` (headless Chrome at
    400px phone width, which keeps text readable with no zoom). The window pans to the quoted line and a lime highlighter sweeps it.
    Captions are two lines max; a " / " in the DISPLAY text marks where a caption chunk breaks.
  - rebuild: `./run_papercut_reel.sh` (`--skip-voice`, `--reshoot` to re-capture the articles).
  - cover: `out/papercut-cover-{mind_blown,facepalm,point_up}.png` (Still `PapercutCover`, props `pose` and `flip`),
    laid out inside the 3:4 profile-grid crop (y 240–1680).
  - Piper: "Codex" → write "Code-ex"; avoid "Open AI's" (heard as "open eyes"), so use "from Open AI".

- **"Hey, I'm Anadi" intro reel** (all 34 character v2 poses, 43s):
  - video: `out/intro-reel.mp4`
  - code: `remotion/src/intro/IntroReel.tsx` · script: `remotion/cfg/intro.json`
  - design system (v2, pixel type + print layout), written up at the top of `IntroReel.tsx`: only the
    character's colours (ink `#0A0A0C`, paper `#F4F4F2`, lime `#D4FF3A`); Jersey 10 for captions/display,
    Silkscreen only for the handle on the end Follow bar (no pose counter); left-aligned on a 70px margin; square corners, no blur/shadows/cards/
    grid; state as type (struck = past, inverted = now); lime block on the spoken word; stepped wipes;
    background-only dither dissolve between chapters. Style frames: `IntroStyleFrame` still,
    `out/intro-style-frames.png`.
  - rebuild: `./run_intro_reel.sh` (or `--skip-voice`). The OpenVoice clone varies per run — check the
    transcript; the shipped take was the best of 4. Piper needs "Anta", not "ANTA".
- **"I didn't draw a single line of this guy" (character build story) reel** (vector character, 41.6s):
  - video: `out/character-story-reel.mp4` · code: `remotion/src/character-story/CharacterStoryReel.tsx` · script: `remotion/cfg/character-story.json`
  - rebuild: `./run_character_story_reel.sh` (or `--skip-voice`)
  - new character effects (`fx` prop on `VectorAnadi`): `draw` self-drawing line art, `ink` fill fade, `build`
    parts drop in one by one, `xray` bones + joints. Reusable in any reel.
  - Remotion `<Img>` gets `max-width: 100%` by default: pass `maxWidth: "none"` for zoomed crops.
- **Vector character (2026-09-28, replaces the cut-out approach):** Anadi as a rigged flat-vector SVG
  (hood down, beard, shades, black hoodie, cargo joggers, white sneakers) in `remotion/src/vector-char/`.
  Real limb animation: arm IK to hand targets, staggered easing with follow-through, breathing/sway,
  planted feet (leg IK), brows, lip-sync from the usual `lipsync.py` tracks, gesture beats on speech.
  15 poses in `rig.ts` (`POSES`). Use `<VectorActor script segs lipsync frame height css />`, where
  script = `[{ from: "<seg>", pose: "talk" }]`. Preview: composition `VectorPreview` →
  `out/vector-character-preview.mp4`. ⚠ Keep single-finger hands as the `point` shape (visible thumb) and
  never vertical with a fist toward the camera: it reads as a rude gesture.
- **Character v3 (2026-09-28, first pass):** the new photoreal look (hood down, all black, cargo pants),
  cut from the two GPT-Image-2 sheets in `character/v3_reference/`. 17 poses, 9 lip-synced
  (`POSES_V3` in `Character.tsx`; use `kit="character_v3"` — pose names differ from v2).
  Rebuild: `cd character/v3 && python3 prep_sheets.py`, then from `character/`:
  `KIT_DIR=v3 python3 build_character.py && KIT_DIR=v3 python3 build_mouths.py`, then copy
  `v3/{illustrated,pixel,pixel_mouths,poses.json}` → `remotion/public/character_v3/`.
  Test clip: `CharacterTalkDemoV3` → `out/character-v3-test.mp4`. Sheet-A's pose row is knee-cropped, so
  point_you/thumbs_up/peace/laptop/coffee/look_up have grafted lower legs. Missing (needs new art):
  talk gesture, point up, shrug, facepalm, mind blown, wave, walk cycle.
- **Character v2 (in progress):** spec `docs/specs/2026-09-27-character-v2-design.md`. Pose build done
  (`character/poses.yaml`, 34 poses), synced to `remotion/public/character_v2` and used via
  `kit="character_v2"`. `public/character` is still v1 until Anadi approves `character/replace_board.png`.
  v1 kit archived in `character/_archive/v1_final/`.

- **"The AI did" (model drift) reel:**
  - video: `out/model-drift-reel.mp4`
  - cover: `out/model-drift-cover-mind_blown.png` (a facepalm alternative is next to it)
  - code: `remotion/src/model-drift/ModelDriftReel.tsx`
  - script: `remotion/cfg/model-drift.json`
  - rebuild everything: `./run_model_drift_reel.sh`, or add `--skip-voice` to only re-render
- **Character kit:** `character/README.md`; rebuild with `character/build.sh`.
