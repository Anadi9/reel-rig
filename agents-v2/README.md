# AI agents v2 — "Your next coworker isn't human"

Combines the three commentary angles: the 49-day timeline + scoreboard (logos get screen time), the
"cute is the strategy" hook (NBC: "It's cute. It's cuddly. And it wants your data."), and the coworker narrative.

- Script + sources: `script.json` · scenes: `src/AgentsV2.tsx` · characters: `src/marks.tsx` · thumbnail: `src/Cover.tsx`
- Rebuild: `../run_agents_v2_reel.sh` (`--skip-voice`, `--cover`) → `../out/agents-v2-reel.mp4`, `../out/agents-v2-cover.png`
- Company logos (xAI, Meta, OpenAI) are mono, from `@lobehub/icons-static-svg` (`src/logos.ts`).
  ⚠ That pack's `meta-text.svg` is the **Llama** wordmark — company names are typeset instead.
- Product marks are the colour characters. The Grok glyph is real; **Jolly and the Dots are illustrations
  drawn from press descriptions**, not official art. Swap in real stills if you want exact likeness.
- Built in the cloud session, where the network blocks news sites, Hugging Face and Pexels, so:
  no article screenshots (headline is typeset as a quote card with outlet + date), voice is **plain Piper,
  not the OpenVoice clone**, and no Whisper transcript check.
  On the Mac: clone `public/vo.wav` with OpenVoice and re-render with `--skip-voice`.
- Remotion uses the Playwright headless shell (`remotion.config.ts`). On the Mac, delete that line.
