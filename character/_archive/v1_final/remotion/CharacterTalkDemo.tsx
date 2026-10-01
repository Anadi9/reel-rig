import React from "react";
import { AbsoluteFill, Audio, interpolate, staticFile, useCurrentFrame } from "remotion";
import { loadFont as loadInter } from "@remotion/google-fonts/InterTight";
import { CharacterActor, type PoseCue } from "./Character";
import { SEG } from "../context-v2/timing";
import { LIPSYNC } from "../context-v2/lipsync";

/**
 * Review demo: the full-body pixel character acting + lip-syncing the first
 * ~19s of the context-v2 voiceover (hook → "Call it PROJECT.md").
 * The face zoom (top right) is for judging the mouth only — not a reel layout.
 */
type SegName = keyof typeof SEG;

const SCRIPT: PoseCue<SegName>[] = [
  { from: "hook1", pose: "talk" },
  { from: "hook2", pose: "hold_paper" },
  { from: "c1a", pose: "laptop" },
  { from: "c1e", pose: "facepalm" },
  { from: "c2a", pose: "shrug" },
  { from: "c2b", pose: "point_up" },
  { from: "c3a", pose: "hold_paper" },
  { from: "c3b", pose: "thumbs_up" },
];

const LINES: Partial<Record<SegName, string>> = {
  hook1: "Every new AI chat forgets your entire project.",
  hook2: "Here's the 📄 one file that fixes it. Template at the end.",
  c1a: "You open a 💬 new chat, and type it all again.",
  c1b: "What you're building.",
  c1c: "Who it's for.",
  c1d: "How you like things done.",
  c1e: "Then tomorrow? New chat. Same speech.",
  c2a: "It's not your prompts.",
  c2b: "The AI just doesn't have your context.",
  c3a: "So, write one file. Plain text.",
  c3b: "Call it PROJECT.md",
};

const FPS = 30;
const LAST: SegName = "c3b";
export const CHAR_TALK_DEMO_DURATION = Math.round(SEG[LAST].next * FPS) + 24;

const { fontFamily: SANS } = loadInter("normal", { weights: ["600"], subsets: ["latin"] });

const lineAt = (t: number) => {
  let cur: SegName | null = null;
  for (const k of Object.keys(LINES) as SegName[]) if (t >= SEG[k].start) cur = k;
  return cur;
};

export const CharacterTalkDemo: React.FC<{ inbetween?: boolean }> = ({ inbetween = true }) => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  const line = lineAt(t);
  const lineIn = line ? interpolate(t - SEG[line].start, [0, 0.12], [0, 1], { extrapolateRight: "clamp" }) : 0;
  const actor = { script: SCRIPT, segs: SEG, lipsync: LIPSYNC, frame, inbetween };
  // face zoom: same actor at ~5x, cropped around the mouth (canvas ≈ 272,126)
  const ZH = 3000;
  const zk = ZH / 560;
  const BOX = 340;
  return (
    <AbsoluteFill style={{ background: "#0B0B0C" }}>
      <AbsoluteFill
        style={{
          backgroundImage:
            "linear-gradient(rgba(255,255,255,0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.05) 1px, transparent 1px)",
          backgroundSize: "54px 54px",
          opacity: 0.6,
        }}
      />
      <div
        style={{
          position: "absolute",
          left: 80,
          right: 80,
          top: 170,
          fontFamily: SANS,
          fontWeight: 600,
          fontSize: 64,
          lineHeight: 1.1,
          letterSpacing: "-0.02em",
          color: "#F2F2F0",
          opacity: lineIn,
        }}
      >
        {line ? LINES[line] : ""}
      </div>
      {/* review zoom */}
      <div style={{ position: "absolute", left: 1080 - 80 - BOX, top: 440, width: BOX, height: BOX, overflow: "hidden", borderRadius: 20, border: "1px solid #2A2A2E", background: "#0B0B0C" }}>
        <CharacterActor {...actor} height={ZH} css={{ left: BOX / 2 - 272 * zk, top: BOX / 2 - 118 * zk }} />
      </div>
      <div style={{ position: "absolute", left: 1080 - 80 - BOX, top: 440 + BOX + 14, width: BOX, textAlign: "center", fontFamily: SANS, fontWeight: 600, fontSize: 26, color: "#6C6C72" }}>
        face zoom (review only)
      </div>
      <CharacterActor {...actor} height={1150} css={{ left: 540 - (540 * 1150) / 560 / 2 - 120, top: 700 }} />
      <Audio src={staticFile("context-v2/vo.wav")} />
    </AbsoluteFill>
  );
};
