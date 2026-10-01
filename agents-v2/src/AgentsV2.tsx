// "Your next coworker isn't human" — AI agents v2 (Grok Bot / Muse / Dots).
// Angle mix: the 49-day timeline + scoreboard (logos get screen time), the "cute is the strategy" hook
// (NBC headline), and the coworker narrative. Brand logos are mono; product marks are the colour characters.
// Design: ink/paper/lime, Jersey 10 captions with a lime block on the spoken word, square corners,
// everything inside the IG safe zone (x 60–940, y 280–1600). All beats key off script line ids (timing.json).
import React from "react";
import { AbsoluteFill, Audio, Easing, Sequence, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import LIPSYNC from "./lipsync.json";
import { VectorBust } from "./VectorBust";
import TIMING from "./timing.json";
import { Check, DOT_COLORS, DotChar, GrokChar, INK, Jolly, LIME, Logo, PAPER, Robot } from "./marks";

export const FPS = 30;
/** The on-screen handle differs per platform: Instagram cut vs X cut. */
const Handle = React.createContext("@THE.ANADI");
type Seg = (typeof TIMING.segments)[number];
const SEGS = TIMING.segments as Seg[];
const seg = (id: string) => SEGS.find((s) => s.id === id)!;
const F = (sec: number) => Math.round(sec * FPS);
/** Frame (relative to `base` seconds) where `word` (nth match) is spoken in line `id`, by char-proportional timing. */
const cueAt = (id: string, word: string, base: number, nth = 0) => {
  const s = seg(id);
  for (const c of s.chunks) {
    const ws = words(c.text);
    const tot = ws.reduce((a, w) => a + wlen(w), 0);
    let acc = 0;
    for (const w of ws) {
      if (w.toLowerCase().replace(/[^a-z0-9$#]/g, "").startsWith(word.toLowerCase())) {
        if (nth-- === 0) return F(c.start + ((c.end - c.start) * acc) / tot - base);
      }
      acc += wlen(w);
    }
  }
  throw new Error(`cue ${id}:${word} not found`);
};
const words = (t: string) => t.split(/\s+/).filter(Boolean);
const wlen = (w: string) => Math.max(1, w.replace(/[^A-Za-z0-9$#]/g, "").length) + 1;

const SCENES = ["hook", "race", "grok", "muse", "dots", "why", "team", "score", "end"] as const;
type Scene = (typeof SCENES)[number];
const DARK: Record<Scene, boolean> = { hook: false, race: true, grok: true, muse: false, dots: true, why: false, team: true, score: false, end: false };
const sceneStart = (sc: Scene) => (sc === "hook" ? 0 : SEGS.find((s) => s.scene === sc)!.start - 0.12);
export const TOTAL_SEC = TIMING.total + 0.6;
const sceneEnd = (sc: Scene) => {
  const i = SCENES.indexOf(sc);
  return i === SCENES.length - 1 ? TOTAL_SEC : sceneStart(SCENES[i + 1]);
};

const JERSEY = "'Jersey 10', sans-serif";
const SILK = "'Silkscreen', monospace";
const BLACK = "'Archivo Black', sans-serif";
const INTER = "'Inter', sans-serif";

const pop = (frame: number, at: number, fps = FPS, damping = 12) => spring({ frame: frame - at, fps, config: { damping, stiffness: 170 } });
const fade = (frame: number, at: number, len = 8) => interpolate(frame, [at, at + len], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
const ease = (frame: number, a: number, b: number, from: number, to: number) =>
  interpolate(frame, [a, b], [from, to], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.bezier(0.2, 0.8, 0.2, 1) });

// ─── captions ──────────────────────────────────────────────────────────────────────────────
type Box = { left: number; top: number; width: number; fontSize: number };
const Captions: React.FC<{ box?: Box }> = ({ box = { left: 70, top: 292, width: 870, fontSize: 86 } }) => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  let chunk: { text: string; start: number; end: number } | null = null;
  let dark = false;
  for (const s of SEGS) {
    for (const c of s.chunks) {
      const nextGap = 0.35;
      if (t >= c.start - 0.05 && t < c.end + nextGap) { chunk = c; dark = DARK[s.scene as Scene]; }
    }
  }
  if (!chunk) return null;
  const ws = words(chunk.text);
  const tot = ws.reduce((a, w) => a + wlen(w), 0);
  let acc = 0;
  const fg = dark ? PAPER : INK;
  return (
    <div style={{ position: "absolute", left: box.left, top: box.top, width: box.width, fontFamily: JERSEY, fontSize: box.fontSize, lineHeight: 0.98, letterSpacing: 0.5 }}>
      {ws.map((w, i) => {
        const ws0 = chunk!.start + ((chunk!.end - chunk!.start) * acc) / tot;
        acc += wlen(w);
        const ws1 = chunk!.start + ((chunk!.end - chunk!.start) * acc) / tot;
        const on = t >= ws0 && t < ws1 + 0.02;
        const said = t >= ws0;
        return (
          <span key={i} style={{ display: "inline-block", marginRight: 18, padding: "0 6px", marginLeft: -6,
            background: on ? LIME : "transparent", color: on ? INK : fg, opacity: said ? 1 : 0.28 }}>{w}</span>
        );
      })}
    </div>
  );
};

// ─── shared bits ───────────────────────────────────────────────────────────────────────────
const Tag: React.FC<{ children: React.ReactNode; dark?: boolean; style?: React.CSSProperties }> = ({ children, dark, style }) => (
  <div style={{ display: "inline-block", fontFamily: SILK, fontSize: 26, padding: "6px 12px", background: dark ? PAPER : INK, color: dark ? INK : PAPER, ...style }}>{children}</div>
);
const Stamp: React.FC<{ text: string; p: number; color?: string; rot?: number; style?: React.CSSProperties }> = ({ text, p, color = LIME, rot = -8, style }) => (
  <div style={{ position: "absolute", fontFamily: JERSEY, fontSize: 92, padding: "4px 22px", background: color, color: INK,
    border: `5px solid ${INK}`, transform: `rotate(${rot}deg) scale(${interpolate(p, [0, 1], [2.2, 1])})`, opacity: Math.min(1, p * 3), ...style }}>{text}</div>
);
/** Launch header: DAY n · DATE + mono company logo + wordmark. */
const LaunchHeader: React.FC<{ day: number; date: string; logo: "xai" | "meta" | "openai"; dark: boolean; frame: number }> = ({ day, date, logo, dark, frame }) => {
  const fg = dark ? PAPER : INK;
  const p = pop(frame, 0);
  return (
    <div style={{ position: "absolute", left: 70, top: 560, display: "flex", alignItems: "center", gap: 26, transform: `translateX(${(1 - p) * -60}px)`, opacity: p }}>
      <div style={{ fontFamily: JERSEY, fontSize: 120, color: INK, background: LIME, padding: "0 18px", lineHeight: 1 }}>DAY {day}</div>
      <div>
        <div style={{ fontFamily: SILK, fontSize: 26, color: fg, opacity: 0.7, marginBottom: 10 }}>{date}</div>
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}><Logo name={logo} size={46} color={fg} /><div style={{ fontFamily: INTER, fontWeight: 800, fontSize: 48, color: fg, letterSpacing: -1 }}>{{ xai: "xAI", meta: "Meta", openai: "OpenAI" }[logo]}</div></div>
      </div>
    </div>
  );
};
/** The 49-day strip: three ticks, a lime progress bar up to `day`. Logos in mono. */
const TimelineStrip: React.FC<{ day: number; dark: boolean; top: number; frame: number; show?: number }> = ({ day, dark, top, frame, show = 3 }) => {
  const fg = dark ? PAPER : INK;
  const X = (d: number) => 90 + (d / 49) * 820;
  const ticks: { d: number; date: string; logo: "xai" | "meta" | "openai" }[] = [
    { d: 0, date: "AUG 11", logo: "xai" }, { d: 28, date: "SEP 8", logo: "meta" }, { d: 49, date: "SEP 29", logo: "openai" }];
  return (
    <div style={{ position: "absolute", left: 0, top, width: 1080, height: 220 }}>
      <div style={{ position: "absolute", left: 90, top: 120, width: 820, height: 6, background: fg, opacity: 0.25 }} />
      <div style={{ position: "absolute", left: 90, top: 120, width: X(day) - 90, height: 6, background: LIME }} />
      {ticks.map((k, i) => {
        if (i >= show) return null;
        const reached = day >= k.d;
        return (
          <div key={k.d} style={{ position: "absolute", left: X(k.d) - 50, top: 0, width: 100, textAlign: "center", opacity: reached ? 1 : 0.35 }}>
            <div style={{ display: "flex", justifyContent: "center", height: 84 }}><Logo name={k.logo} size={74} color={fg} /></div>
            <div style={{ width: 22, height: 22, margin: "17px auto 0", background: reached ? LIME : dark ? INK : PAPER, border: `4px solid ${fg}` }} />
            <div style={{ fontFamily: SILK, fontSize: 22, color: fg, marginTop: 12 }}>{k.date}</div>
          </div>
        );
      })}
    </div>
  );
};

// ─── narrator: the vector character bust, bottom-left, lip-synced to the voiceover ─────────
// VectorBust is a redraw of the rig (src/VectorBust.tsx); track from avatar/lipsync.py. Face stays above the IG caption block.
export const NARRATOR = { left: 10, top: 1330, width: 500 };
const Narrator: React.FC<{ pos?: { left: number; top: number; width: number } }> = ({ pos = NARRATOR }) => {
  const frame = useCurrentFrame();
  const i = Math.min(frame, LIPSYNC.visemes.length - 1);
  const v = LIPSYNC.visemes[i];
  const bob = LIPSYNC.bob[i] || (i > 0 && LIPSYNC.bob[i - 1]) ? -5 : 0;
  const talking = v !== "rest";
  const tilt = Math.sin(frame / 23) * (talking ? 2.2 : 0.8);
  const enter = spring({ frame, fps: FPS, config: { damping: 14 } });
  return (
    <div style={{ position: "absolute", left: pos.left, top: pos.top + bob + (1 - enter) * 320 }}>
      <VectorBust width={pos.width} viseme={v} brow={LIPSYNC.brow[i] === 1} tilt={tilt} />
    </div>
  );
};

// ─── scenes ────────────────────────────────────────────────────────────────────────────────
const HookScene: React.FC = () => {
  const frame = useCurrentFrame();
  const h1 = seg("h1"), h2 = seg("h2");
  const cardP = pop(frame, 2, FPS, 14);
  const hl = ease(frame, cueAt("h1", "and", 0), cueAt("h1", "data", 0) + 8, 0, 1);
  const stampP = pop(frame, F(h2.start) + 4, FPS, 10);
  const chips = ["INBOX", "CALENDAR", "CARD"];
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", left: 70, top: 600, width: 860, background: "#fff", border: `4px solid ${INK}`, padding: "30px 36px 40px",
        transform: `translateY(${(1 - cardP) * 80}px) rotate(${(1 - cardP) * -3}deg)`, opacity: Math.min(1, cardP * 2) }}>
        <Tag>NBC NEWS · SEP 24, 2026</Tag>
        <div style={{ fontFamily: INTER, fontWeight: 800, fontSize: 70, lineHeight: 1.08, color: INK, marginTop: 22, letterSpacing: -1.5 }}>
          It’s cute. It’s cuddly.{" "}
          <span style={{ backgroundImage: `linear-gradient(${LIME}, ${LIME})`, backgroundRepeat: "no-repeat", backgroundSize: `${hl * 100}% 100%` }}>
            And it wants your data.</span>
        </div>
        <div style={{ fontFamily: INTER, fontSize: 26, color: "#555", marginTop: 18 }}>On Meta’s new AI agent, Muse</div>
      </div>
      {frame >= F(h2.start) && <Stamp text="REAL HEADLINE" p={stampP} style={{ right: 70, top: 560 }} rot={6} />}
      <div style={{ position: "absolute", left: 560, top: 1010 }}><Jolly size={360} frame={frame} wave={frame < F(h1.start) + 30 ? 1 : 0} /></div>
      {chips.map((c, i) => {
        const at = cueAt("h1", "data", 0) - 6 + i * 5;
        const p = ease(frame, at, at + 16, 0, 1);
        const x0 = 90 + i * 150, y0 = 1060 + i * 80;
        return (
          <div key={c} style={{ position: "absolute", left: interpolate(p, [0, 1], [x0, 700]), top: interpolate(p, [0, 1], [y0, 1220]),
            opacity: frame < at ? 0 : 1 - p, transform: `scale(${1 - p * 0.6})`, fontFamily: SILK, fontSize: 26, padding: "8px 12px", background: INK, color: PAPER }}>{c}</div>
        );
      })}
    </AbsoluteFill>
  );
};

const RaceScene: React.FC = () => {
  const frame = useCurrentFrame();
  const base = sceneStart("race");
  const count = Math.round(ease(frame, 6, cueAt("h3", "same", base) + 6, 0, 49));
  const winAt = cueAt("h3", "cutest", base);
  const qP = pop(frame, winAt, FPS, 9);
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", left: 70, top: 560, fontFamily: JERSEY, color: PAPER, lineHeight: 0.85 }}>
        <div style={{ fontSize: 330, color: LIME }}>{count}</div>
        <div style={{ fontSize: 96 }}>DAYS. SAME BET.</div>
      </div>
      <TimelineStrip day={count} dark top={1010} frame={frame} />
      {frame >= winAt && (
        <div style={{ position: "absolute", left: 70, top: 1250, display: "flex", alignItems: "center", gap: 24, transform: `scale(${qP})`, transformOrigin: "left center" }}>
          <div style={{ fontFamily: JERSEY, fontSize: 84, background: LIME, color: INK, padding: "0 18px" }}>WINNER: ???</div>
          <div style={{ fontFamily: SILK, fontSize: 24, color: PAPER, opacity: 0.7 }}>STAY FOR THE<br />SCOREBOARD</div>
        </div>
      )}
    </AbsoluteFill>
  );
};

const GrokScene: React.FC = () => {
  const frame = useCurrentFrame();
  const base = sceneStart("grok");
  const inP = pop(frame, cueAt("a1", "grok", base) - 4, FPS, 11);
  const lidAt = cueAt("a1", "keeps", base) - 2;
  const lid = ease(frame, lidAt, lidAt + 14, 0, 1);
  const tasks = ["Inbox triaged", "CRM updated", "Bug fixed"];
  return (
    <AbsoluteFill>
      <LaunchHeader day={0} date="AUG 11 · BETA" logo="xai" dark frame={frame} />
      <div style={{ position: "absolute", left: 90, top: 820, transform: `scale(${inP})`, transformOrigin: "center" }}>
        <GrokChar size={300} frame={frame} working={frame > lidAt} />
        <div style={{ fontFamily: SILK, fontSize: 26, color: PAPER, textAlign: "center", marginTop: 18 }}>GROK BOT</div>
      </div>
      {/* laptop: the lid folds shut, the bot keeps ticking tasks */}
      <div style={{ position: "absolute", left: 540, top: 820, width: 380, opacity: fade(frame, cueAt("a1", "it", base) - 6) }}>
        <div style={{ height: 250, transformOrigin: "bottom center", transform: `perspective(900px) rotateX(${lid * 86}deg)`,
          background: "#1C1C20", border: `6px solid #3A3A40`, borderBottom: "none", padding: 22, boxSizing: "border-box" }}>
          <div style={{ fontFamily: SILK, fontSize: 20, color: PAPER, opacity: 0.6 }}>YOUR LAPTOP</div>
        </div>
        <div style={{ height: 20, background: "#3A3A40", width: 420, marginLeft: -20 }} />
        <div style={{ fontFamily: SILK, fontSize: 24, color: lid > 0.9 ? LIME : PAPER, marginTop: 16, opacity: lid > 0.9 ? 1 : 0 }}>LID CLOSED. STILL WORKING.</div>
      </div>
      {tasks.map((tk, i) => {
        const at = lidAt + 12 + i * 8;
        return (
          <div key={tk} style={{ position: "absolute", left: 590, top: 1190 + i * 72, display: "flex", alignItems: "center", gap: 16, opacity: fade(frame, at, 5) }}>
            <Check size={44} color={LIME} p={ease(frame, at, at + 8, 0, 1)} />
            <div style={{ fontFamily: JERSEY, fontSize: 58, color: PAPER }}>{tk}</div>
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

const MuseScene: React.FC = () => {
  const frame = useCurrentFrame();
  const base = sceneStart("muse");
  const jIn = pop(frame, cueAt("b1", "muse", base) - 2, FPS, 10);
  const nameP = pop(frame, cueAt("b1", "jolly", base), FPS, 9);
  const keyAt = F(seg("b2").start - base);
  const k = ease(frame, keyAt + 4, keyAt + 22, 0, 1);
  const jSize = interpolate(k, [0, 1], [400, 240]);
  const swing = Math.sin((frame - keyAt) / 7) * 6 * k;
  return (
    <AbsoluteFill>
      <LaunchHeader day={28} date="SEP 8 · APP STORE #1" logo="meta" dark={false} frame={frame} />
      <div style={{ position: "absolute", left: 600 - jSize / 2, top: interpolate(k, [0, 1], [860, 1010]), transform: `scale(${jIn}) rotate(${swing}deg)`, transformOrigin: "50% -30%" }}>
        {/* keychain: ring + chain + charm frame */}
        {k > 0 && (
          <svg style={{ position: "absolute", left: jSize / 2 - 60, top: -190 * k, opacity: k }} width="120" height="200" viewBox="0 0 120 200">
            <circle cx="60" cy="40" r="32" fill="none" stroke="#9A9AA2" strokeWidth="9" />
            {[0, 1, 2, 3].map((i) => <ellipse key={i} cx="60" cy={86 + i * 26} rx="8" ry="13" fill="none" stroke="#9A9AA2" strokeWidth="6" />)}
          </svg>
        )}
        <div style={{ border: k > 0 ? `${8 * k}px solid ${INK}` : "none", borderRadius: 60 * k, padding: 24 * k, background: k > 0 ? "#fff" : "transparent" }}>
          <Jolly size={jSize} frame={frame} wave={frame < cueAt("b1", "jolly", base) + 30 ? 1 : 0} />
        </div>
      </div>
      {frame >= cueAt("b1", "jolly", base) && k < 0.5 && (
        <div style={{ position: "absolute", left: 640, top: 1230, transform: `scale(${nameP}) rotate(4deg)`, fontFamily: JERSEY, fontSize: 80, background: LIME, color: INK, padding: "0 18px", border: `4px solid ${INK}` }}>“JOLLY”</div>
      )}
      {k > 0 && (
        <div style={{ position: "absolute", left: 560, top: 1400, opacity: k }}>
          <Tag>MUSE CHARM</Tag>
          <div style={{ fontFamily: JERSEY, fontSize: 54, color: INK, marginTop: 8 }}>LABUBU × TAMAGOTCHI</div>
        </div>
      )}
    </AbsoluteFill>
  );
};

const DOT_NAMES = ["dot", "Biscuit", "Captain"];
const DotsScene: React.FC = () => {
  const frame = useCurrentFrame();
  const base = sceneStart("dots");
  const inAt = cueAt("c1", "dots", base) - 4;
  const nameAt = cueAt("c1", "bubbles", base) - 4;
  return (
    <AbsoluteFill>
      <LaunchHeader day={49} date="SEP 29 · DEVDAY" logo="openai" dark frame={frame} />
      {DOT_NAMES.map((n, i) => {
        const p = pop(frame, inAt + i * 5, FPS, 9);
        const x = 110 + i * 300, y = 860 + (i % 2) * 70;
        const typed = Math.max(0, Math.min(n.length, Math.floor((frame - nameAt - i * 6) / 1.3)));
        return (
          <div key={n} style={{ position: "absolute", left: x, top: y + (1 - p) * 300, opacity: Math.min(1, p * 2) }}>
            <DotChar size={240} frame={frame} color={DOT_COLORS[i]} seed={i} />
            {frame >= nameAt + i * 6 && (
              <div style={{ marginTop: 14, marginLeft: 20, display: "inline-block", fontFamily: JERSEY, fontSize: 58, color: INK, background: PAPER, padding: "0 14px", minWidth: 40 }}>
                {n.slice(0, typed)}<span style={{ opacity: frame % 16 < 8 ? 1 : 0 }}>|</span>
              </div>
            )}
          </div>
        );
      })}
      <div style={{ position: "absolute", left: 70, top: 760, fontFamily: SILK, fontSize: 24, color: PAPER, opacity: 0.7 * fade(frame, nameAt) }}>“YOUR DOT” → RENAME IT ANYTHING</div>
    </AbsoluteFill>
  );
};

const WhyScene: React.FC = () => {
  const frame = useCurrentFrame();
  const base = sceneStart("why");
  const robotAt = cueAt("d1", "robot", base) - 18;
  const friendAt = F(seg("d2").start - base);
  const items = ["INBOX", "CALENDAR", "CARD"];
  const swap = ease(frame, friendAt - 4, friendAt + 8, 0, 1);
  return (
    <AbsoluteFill>
      {items.map((it, i) => {
        const appear = cueAt("d1", i === 0 ? "inbox" : i === 1 ? "and" : "card", base) - 6;
        const toRobot = ease(frame, robotAt + i * 3, robotAt + 12 + i * 3, 0, 1);
        const bounce = frame > robotAt + 12 && frame < friendAt ? Math.sin(((frame - robotAt - 12) / 10) * Math.PI) * 30 : 0;
        const toFriend = ease(frame, friendAt + 4 + i * 4, friendAt + 18 + i * 4, 0, 1);
        const x = 70 + i * 290;
        const y = 600 + toRobot * 220 - Math.abs(bounce) + toFriend * 420;
        const tx = interpolate(toFriend, [0, 1], [interpolate(toRobot, [0, 1], [x, [430, 590, 820][i]]), 560 + i * 90]);
        return (
          <div key={it} style={{ position: "absolute", left: tx, top: y, opacity: fade(frame, appear, 6) * (1 - toFriend * 0.85),
            transform: `scale(${1 - toFriend * 0.5}) rotate(${(i - 1) * 4}deg)`, fontFamily: JERSEY, fontSize: 70, background: INK, color: PAPER, padding: "6px 22px" }}>{it}</div>
        );
      })}
      <div style={{ position: "absolute", left: 70, top: 900, fontFamily: BLACK, fontSize: 200, lineHeight: 0.9, color: INK, letterSpacing: -6,
        opacity: 1 - fade(frame, robotAt - 8, 6), transform: `scale(${pop(frame, 0)})`, transformOrigin: "left center" }}>WHY<br /><span style={{ background: LIME, padding: "0 14px" }}>CUTE?</span></div>
      {/* robot ↔ friends */}
      <div style={{ position: "absolute", left: 560, top: 960, opacity: (1 - swap) * fade(frame, robotAt - 4, 6) }}>
        <Robot size={300} frame={frame} />
        {frame > robotAt + 14 && <Stamp text="NOPE" p={pop(frame, robotAt + 14, FPS, 10)} color="#FF5A4E" rot={-10} style={{ left: 200, top: -60 }} />}
      </div>
      {swap > 0 && (
        <div style={{ position: "absolute", left: 300, top: 1040, width: 640, display: "flex", alignItems: "flex-end", justifyContent: "flex-end", gap: 24,
          transform: `scale(${swap})`, transformOrigin: "center bottom" }}>
          <GrokChar size={190} frame={frame} />
          <Jolly size={250} frame={frame} wave={1} />
          <DotChar size={200} frame={frame} color={DOT_COLORS[0]} />
        </div>
      )}
      {swap > 0.5 && <Stamp text="FRIEND" p={pop(frame, friendAt + 10, FPS, 10)} rot={-6} style={{ left: 600, top: 960 }} />}
    </AbsoluteFill>
  );
};

const TeamScene: React.FC = () => {
  const frame = useCurrentFrame();
  const base = sceneStart("team");
  const e2 = F(seg("e2").start - base), e3 = F(seg("e3").start - base);
  const bossAt = cueAt("e1", "bot", base) - 4;
  const subs = ["INBOX", "EXPENSES", "RECRUITING"];
  const phase = frame < e2 ? 0 : frame < e3 ? 1 : 2;
  const smbAt = cueAt("e2", "meta", base) - 4;
  return (
    <AbsoluteFill>
      {phase === 0 && (
        <>
          <div style={{ position: "absolute", left: 410, top: 560, transform: `scale(${pop(frame, bossAt)})` }}>
            <GrokChar size={260} frame={frame} working />
            <div style={{ fontFamily: JERSEY, fontSize: 52, color: INK, background: LIME, textAlign: "center", marginTop: 14, padding: "0 10px" }}>CHIEF OF STAFF</div>
          </div>
          {subs.map((s, i) => {
            const at = cueAt("e1", "has", base) + i * 5;
            const p = pop(frame, at);
            const x = 110 + i * 300;
            return (
              <React.Fragment key={s}>
                <svg style={{ position: "absolute", left: 0, top: 0 }} width="1080" height="1920">
                  <line x1="540" y1="900" x2={x + 80} y2="1070" stroke={PAPER} strokeOpacity={0.4 * p} strokeWidth="4" strokeDasharray="10 10" />
                </svg>
                <div style={{ position: "absolute", left: x, top: 1070, transform: `scale(${p})`, textAlign: "center", width: 160 }}>
                  <GrokChar size={160} frame={frame + i * 11} working />
                  <div style={{ fontFamily: SILK, fontSize: 22, color: PAPER, marginTop: 10 }}>{s}</div>
                </div>
              </React.Fragment>
            );
          })}
        </>
      )}
      {phase === 1 && (
        <>
          <div style={{ position: "absolute", left: 70, top: 600, display: "flex", alignItems: "center", gap: 18 }}>
            <Logo name="openai" size={52} color={PAPER} /><Tag dark>TEAMS OF DOTS · COMING</Tag>
          </div>
          {[0, 1, 2, 3, 4].map((i) => (
            <div key={i} style={{ position: "absolute", left: 70 + i * 178, top: 700, transform: `translateY(${(1 - pop(frame, e2 + i * 3)) * 200}px)` }}>
              <DotChar size={150} frame={frame} color={DOT_COLORS[i]} seed={i} />
            </div>
          ))}
          <div style={{ position: "absolute", left: 70, top: 1010, opacity: fade(frame, smbAt), display: "flex", alignItems: "center", gap: 18 }}>
            <Logo name="meta" size={52} color={PAPER} /><Tag dark>MUSE FOR SMALL BUSINESS · SEP 29</Tag>
          </div>
          <div style={{ position: "absolute", left: 70, top: 1100, opacity: fade(frame, smbAt), display: "flex", gap: 30, alignItems: "flex-start" }}>
            <Jolly size={230} frame={frame} />
            <div style={{ display: "flex", flexWrap: "wrap", gap: 14, width: 580, marginTop: 20 }}>
              {["Shopify", "Stripe", "QuickBooks", "Slack", "Canva", "Notion"].map((t, i) => (
                <div key={t} style={{ fontFamily: JERSEY, fontSize: 54, color: PAPER, border: `3px solid ${PAPER}`, padding: "0 16px", opacity: fade(frame, smbAt + 6 + i * 3, 5) }}>{t}</div>
              ))}
            </div>
          </div>
        </>
      )}
      {phase === 2 && (() => {
        const rows: { who: React.ReactNode; name: string; role: string }[] = [
          { who: <GrokChar size={96} frame={frame} />, name: "Grok Bot", role: "chief of staff" },
          { who: <Jolly size={92} frame={frame} />, name: "Jolly", role: "small business ops" },
          { who: <DotChar size={92} frame={frame} color={DOT_COLORS[1]} />, name: "Biscuit", role: "your dot" },
        ];
        const nh = cueAt("e3", "not", base) - 2, ad = cueAt("e3", "adorable", base) - 4;
        return (
          <>
            <div style={{ position: "absolute", left: 70, top: 600, width: 860, background: "#16161A", border: `3px solid #2E2E34` }}>
              <div style={{ fontFamily: SILK, fontSize: 24, color: PAPER, opacity: 0.7, padding: "18px 26px", borderBottom: "3px solid #2E2E34" }}># your-team · 3 members</div>
              {rows.map((r, i) => (
                <div key={r.name} style={{ display: "flex", alignItems: "center", gap: 28, padding: "20px 26px", opacity: fade(frame, e3 + i * 4, 6) }}>
                  <div style={{ width: 110, display: "flex", justifyContent: "center" }}>{r.who}</div>
                  <div>
                    <div style={{ fontFamily: JERSEY, fontSize: 66, color: PAPER, lineHeight: 1 }}>{r.name}</div>
                    <div style={{ fontFamily: SILK, fontSize: 20, color: PAPER, opacity: 0.55 }}>{r.role} · online 24/7</div>
                  </div>
                </div>
              ))}
            </div>
            {frame >= nh && <Stamp text="NOT HUMAN" p={pop(frame, nh, FPS, 10)} color="#FF5A4E" rot={-7} style={{ left: 150, top: 1150 }} />}
            {frame >= ad && <Stamp text="ADORABLE" p={pop(frame, ad, FPS, 10)} rot={5} style={{ left: 560, top: 1260 }} />}
          </>
        );
      })()}
    </AbsoluteFill>
  );
};

const ScoreScene: React.FC = () => {
  const frame = useCurrentFrame();
  const base = sceneStart("score");
  const appAt = cueAt("f1", "muse", base);
  const stockAt = cueAt("f1", "stock", base);
  const priceAt = F(seg("f2").start - base);
  const strikeAt = cueAt("f2", "to", base, 0);
  const dotAt = F(seg("f3").start - base) + 4;
  const cols: { logo: "xai" | "meta" | "openai"; mark: React.ReactNode; name: string }[] = [
    { logo: "xai", mark: <GrokChar size={70} frame={frame} />, name: "GROK BOT" },
    { logo: "meta", mark: <Jolly size={66} frame={frame} />, name: "MUSE" },
    { logo: "openai", mark: <DotChar size={66} frame={frame} color={DOT_COLORS[0]} />, name: "DOTS" },
  ];
  const ROWS = 3;
  const cell = (row: number, col: number): React.ReactNode => {
    if (row === 0) return col === 1 ? <span style={{ background: LIME, padding: "0 8px" }}>#1</span> : <span style={{ opacity: 0.3 }}>—</span>;
    if (row === 1) return col === 1 ? <span style={{ fontSize: 44 }}>BEST MONTH SINCE 2013</span> : <span style={{ opacity: 0.3, fontSize: 40 }}>PRIVATE</span>;
    if (col === 0) return (<span><span style={{ position: "relative", opacity: 0.55 }}>$300
      <span style={{ position: "absolute", left: -4, right: -4, top: "52%", height: 6, background: "#FF5A4E", transformOrigin: "left", transform: `scaleX(${ease(frame, strikeAt, strikeAt + 8, 0, 1)})` }} /></span>
      {frame >= strikeAt + 4 && <span style={{ background: LIME, padding: "0 8px", marginLeft: 10 }}>$30</span>}</span>);
    if (col === 1) return <span style={{ fontSize: 46 }}>FREE TIER</span>;
    return frame >= dotAt ? <span style={{ fontSize: 46, background: LIME, padding: "0 6px" }}>1st INCL. W/ PRO</span> : <span style={{ opacity: 0.3 }}>…</span>;
  };
  const rowAt = [appAt, stockAt, priceAt];
  const rowName = ["APP STORE", "STOCK", "PRICE"];
  const lead = pop(frame, stockAt + 20, FPS, 10);
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", left: 70, top: 600, width: 880, border: `4px solid ${INK}`, background: "#fff" }}>
        <div style={{ display: "grid", gridTemplateColumns: "200px 1fr 1fr 1fr", borderBottom: `4px solid ${INK}` }}>
          <div style={{ fontFamily: JERSEY, fontSize: 52, padding: "18px 16px", alignSelf: "center" }}>SCORE</div>
          {cols.map((c, i) => (
            <div key={c.name} style={{ padding: "16px 10px", borderLeft: `3px solid ${INK}`, display: "flex", flexDirection: "column", alignItems: "center", gap: 8,
              background: i === 1 && lead > 0.05 ? LIME : "transparent" }}>
              <Logo name={c.logo} size={44} color={INK} />
              <div style={{ height: 78, display: "flex", alignItems: "flex-end" }}>{c.mark}</div>
              <div style={{ fontFamily: SILK, fontSize: 18 }}>{c.name}</div>
            </div>
          ))}
        </div>
        {Array.from({ length: ROWS }).map((_, r) => (
          <div key={r} style={{ display: "grid", gridTemplateColumns: "200px 1fr 1fr 1fr", borderTop: r ? `3px solid ${INK}` : "none", opacity: fade(frame, rowAt[r] - 4, 6), minHeight: 150 }}>
            <div style={{ fontFamily: SILK, fontSize: 22, padding: "0 16px", alignSelf: "center" }}>{rowName[r]}</div>
            {[0, 1, 2].map((c) => (
              <div key={c} style={{ borderLeft: `3px solid ${INK}`, display: "flex", alignItems: "center", justifyContent: "center", textAlign: "center",
                fontFamily: JERSEY, fontSize: 64, lineHeight: 0.95, padding: "10px 12px", color: INK }}>{cell(r, c)}</div>
            ))}
          </div>
        ))}
      </div>
      {lead > 0.05 && <Stamp text="LEADING" p={lead} rot={-6} style={{ left: 520, top: 528, fontSize: 70 }} />}
      <div style={{ position: "absolute", left: 70, top: 1250, fontFamily: SILK, fontSize: 20, color: INK, opacity: 0.55, width: 860 }}>
        SOURCES: CNBC, BLOOMBERG, NBC, X.AI, ENGADGET, TECHCRUNCH · SEP 2026
      </div>
    </AbsoluteFill>
  );
};

const EndScene: React.FC = () => {
  const frame = useCurrentFrame();
  const handle = React.useContext(Handle);
  const base = sceneStart("end");
  const whoAt = cueAt("g1", "who", base) - 4;
  const labels = ["GROK BOT", "MUSE", "DOTS"];
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", left: 70, top: 580, fontFamily: BLACK, fontSize: 168, lineHeight: 0.9, color: INK, letterSpacing: -4,
        transform: `scale(${pop(frame, whoAt)})`, transformOrigin: "left center" }}>WHO<br /><span style={{ background: LIME, padding: "0 14px" }}>WINS?</span></div>
      <div style={{ position: "absolute", left: 70, top: 920, width: 880, display: "flex", justifyContent: "space-between", alignItems: "flex-end" }}>
        {[<GrokChar key="g" size={200} frame={frame} />, <Jolly key="j" size={240} frame={frame} wave={frame > whoAt ? 1 : 0} />, <DotChar key="d" size={210} frame={frame} color={DOT_COLORS[0]} />].map((el, i) => (
          <div key={i} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 10, transform: `translateY(${(1 - pop(frame, 2 + i * 5)) * 300}px)` }}>
            {el}
            <div style={{ fontFamily: JERSEY, fontSize: 56, color: PAPER, background: INK, padding: "0 14px", opacity: fade(frame, 4 + i * 6) }}>{labels[i]}</div>
          </div>
        ))}
      </div>
      <div style={{ position: "absolute", left: 580, top: 1340, width: 360, display: "flex", flexDirection: "column", alignItems: "flex-start", gap: 18, opacity: fade(frame, whoAt + 10) }}>
        <div style={{ fontFamily: JERSEY, fontSize: 60, color: INK, whiteSpace: "nowrap" }}>COMMENT BELOW ↓</div>
        <div style={{ fontFamily: SILK, fontSize: 26, background: INK, color: LIME, padding: "10px 16px" }}>{handle}</div>
      </div>
    </AbsoluteFill>
  );
};

const SCENE_COMP: Record<Scene, React.FC> = { hook: HookScene, race: RaceScene, grok: GrokScene, muse: MuseScene, dots: DotsScene, why: WhyScene, team: TeamScene, score: ScoreScene, end: EndScene };

/** All scenes on a 1080×1920 stage (backgrounds + stepped wipes), without narrator or captions. */
const Stage: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const durationInFrames = Math.ceil(TOTAL_SEC * fps);
  return (
    <AbsoluteFill style={{ background: PAPER, width: 1080, height: 1920 }}>
      {SCENES.map((sc) => {
        const from = F(sceneStart(sc)), to = sc === "end" ? durationInFrames : F(sceneEnd(sc));
        const C = SCENE_COMP[sc];
        // stepped wipe in: the new scene's background drops in 4 bands
        const wipe = (f: number) => Math.min(1, Math.floor(((f - from) / 6) * 4 + 1) / 4);
        return (
          <Sequence key={sc} from={from} durationInFrames={to - from} name={sc}>
            <AbsoluteFill style={{ background: DARK[sc] ? INK : PAPER, clipPath: sc === "hook" ? undefined : `inset(0 0 ${(1 - wipe(frame)) * 100}% 0)` }}>
              <C />
            </AbsoluteFill>
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};

export const AgentsV2: React.FC = () => (
  <AbsoluteFill style={{ background: PAPER }}>
    <Stage />
    <Narrator />
    <Captions />
    <Audio src={staticFile("vo.wav")} />
  </AbsoluteFill>
);

// ─── landscape (X / YouTube, 1920×1080) ──────────────────────────────────────────────────────
// Left panel: captions + narrator bust. Right: a 1080×1080 window onto the portrait stage's action band
// (y 520–1600: everything between the portrait captions and the portrait bust slot).
const BAND_TOP = 520;
export const AgentsV2Landscape: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  const cur = [...SCENES].reverse().find((sc) => t >= sceneStart(sc)) ?? "hook";
  const dark = DARK[cur];
  return (
    <AbsoluteFill style={{ background: dark ? INK : PAPER }}>
      <div style={{ position: "absolute", left: 840, top: 0, width: 1080, height: 1080, overflow: "hidden" }}>
        <div style={{ position: "absolute", left: 0, top: -BAND_TOP, width: 1080, height: 1920 }}><Handle.Provider value="@ANADI_THAKUR"><Stage /></Handle.Provider></div>
      </div>
      <div style={{ position: "absolute", left: 836, top: 60, width: 4, height: 960, background: dark ? PAPER : INK, opacity: 0.12 }} />
      <Captions box={{ left: 64, top: 64, width: 720, fontSize: 76 }} />
      <Narrator pos={{ left: 150, top: 470, width: 520 }} />
      <div style={{ position: "absolute", left: 64, top: 1010, fontFamily: SILK, fontSize: 22, padding: "6px 12px", background: dark ? PAPER : INK, color: dark ? INK : LIME }}>@ANADI_THAKUR · AI NEWS</div>
      <Audio src={staticFile("vo.wav")} />
    </AbsoluteFill>
  );
};
