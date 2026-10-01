# Reel — "The Wrapper Test" (outage-hook version)

Feed: personal @the.anadi · Talking-head voiceover (cloned voice) over motion graphics.
Composition: WrapperTestReel (remotion/src/wrapper-test/WrapperTestReel.tsx)

## Why now
Sept 3 2026 — ChatGPT, Claude, Grok and Gemini all went down at once (confirmed by
Gizmodo, 9to5Google, LadBible, Daily Voice). Live, real, and exactly the proof
point the Wrapper Test's whole premise needs: if a product dies when the
model API dies, it was never a product.

## VO script (also remotion/cfg/wrapper-test.json)

| Beat | Line |
|---|---|
| HOOK | "Right now, ChatGPT, Claude, Grok, and Gemini are all down. At the same time." |
| PAIN | "If your product just went down with them, that's not bad luck. That's the truth about what you built." |
| SETUP | "It's just a wrapper. A UI stitched onto someone else's model." |
| PAYOFF | "I built a free three minute test, thirteen questions, that scores exactly how exposed you are. No signup, instant report." |
| CTA | "It's called The Wrapper Test. Link in bio." |

~30s at Piper's natural pace. Real per-segment timing comes from
`make_props.py` after synthesis — the composition sizes every scene off the
actual audio, nothing is hardcoded.

## Visual system
Reused the myths/kit.tsx + chatbot-vs-agent/primitives.tsx toolkit (same
procedural palette/type system as MythsFacts, no stock footage, nothing to
fetch): near-black bg, Space Grotesk headlines, JetBrains Mono for
terminal/status text, cyan + red accents, a soft particle field for texture.

- HOOK: a "MODEL STATUS" ticker — ChatGPT / Claude / Grok / Gemini flip to
  "● DOWN" in red, one by one, timed to the VO.
- PAIN: word-by-word reveal, punchline lands in red.
- SETUP: "WRAPPER." stamped on screen.
- PAYOFF: three stat chips — FREE / 3 MIN / 1 SCORE.
- CTA: end card — "THE WRAPPER TEST", anadithakur.in/teardown, link in bio.
- Whisper captions burned in throughout (bottom third, mono chip).

## To render
One command, from a normal Terminal (not through the phone/desktop bridge —
Piper, the OpenVoice venv and Remotion's compositor all need to run natively
on this Mac):

    ./run_wrapper_test_reel.sh

Output: `remotion/out/wrapper-test-reel.mp4` — opens automatically when done.
Stops there; post it yourself.

## If something's missing
- `piper: command not found` → `pip install piper-tts --break-system-packages`
- OpenVoice import error → re-check the `openvoice/.venv` per references/setup.md
- `faster_whisper` missing → `pip install faster-whisper --break-system-packages`
- Want a quick draft without the cloned voice → run `build_voice.py`'s steps
  manually and skip the `clone_voice.py` call, point `voice_cloned.wav` at
  the raw Piper output instead.

## To tweak the script later
Edit `remotion/cfg/wrapper-test.json` (five lines, one per beat) and re-run
the script — everything downstream (timing, captions, render) recalculates
automatically.
