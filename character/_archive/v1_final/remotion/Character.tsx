import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, Easing } from "remotion";
import { loadFont as loadInter } from "@remotion/google-fonts/InterTight";
import { speechAt, type Lipsync, type Viseme } from "../avatar/PixelAvatar";

/**
 * Anadi's full-body character (12 poses, two styles), built by
 * ~/reel-rig/character/build_character.py. All poses share one canvas (540×560)
 * with the feet on the same baseline and the face (mouth) on the same point, so switching
 * poses doesn't make the head jump.
 */
export const POSES = [
  "idle", "talk", "point_up", "hold_paper", "point_down", "wave",
  "laptop", "phone", "facepalm", "shrug", "mind_blown", "thumbs_up",
] as const;
export type Pose = (typeof POSES)[number];
export type CharStyle = "illustrated" | "pixel";

const CW = 540;
const CH = 560;
const SEAM = 290; // canvas row inside the hoodie where the upper body splits off (breathing/nod)
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

/**
 * Poses with lip-sync mouths (~/reel-rig/character/build_mouths.py → public/character/pixel_mouths).
 * mind_blown keeps its own drawn open "O" mouth, so it has none.
 */
const TALKING_POSES: ReadonlySet<Pose> = new Set(POSES.filter((p) => p !== "mind_blown"));

/**
 * t = frames since the current pose started (drives the pop), frame = absolute (drives breathing).
 * Pixel style snaps its motion to the 2px pixel grid so it stays crisp.
 * viseme: speech shape from a lipsync.py track (pixel style only; "rest" = the pose's own mouth).
 * nod: 1-cell dip on stressed syllables (from the same track).
 */
export const Character: React.FC<{
  pose: Pose;
  style?: CharStyle;
  height?: number;
  sincePose?: number;
  frame: number;
  flip?: boolean;
  viseme?: Viseme;
  nod?: boolean;
  css?: React.CSSProperties;
}> = ({ pose, style = "pixel", height = 900, sincePose = 99, frame, flip, viseme = "rest", nod = false, css }) => {
  const k = height / CH;
  const w = CW * k;
  // pose change: quick squash → overshoot → settle, anchored at the feet
  const sy = interpolate(sincePose, [0, 2, 6, 10], [0.94, 1.035, 0.99, 1], clamp);
  const sx = interpolate(sincePose, [0, 2, 6, 10], [1.04, 0.98, 1.005, 1], clamp);
  // Breathing + nod move only the upper body, so the feet stay planted. The sprite is drawn
  // twice, split at the hoodie (SEAM): the top half shifts by one pixel cell and the bottom
  // half starts one cell higher, so the seam row stretches instead of leaving a gap.
  // Breathing: chest up 1 cell for half of a ~1.4s cycle. Nod: down 1 cell.
  const cell = 2 * k;
  const lift = (Math.sin((frame / 42) * Math.PI * 2) > 0 ? -cell : 0) + (nod ? cell : 0);
  const showMouth = style === "pixel" && viseme !== "rest" && TALKING_POSES.has(pose);
  const layer: React.CSSProperties = {
    position: "absolute",
    left: 0,
    top: 0,
    width: w,
    height,
    imageRendering: style === "pixel" ? "pixelated" : "auto",
  };
  const src = staticFile(`character/${style}/${pose}.png`);
  return (
    <div style={{ position: "absolute", width: w, height, ...css }}>
      <div
        style={{
          position: "absolute",
          width: w,
          height,
          transformOrigin: "50% 98%",
          transform: `scale(${flip ? -sx : sx}, ${sy})`,
        }}
      >
        <Img src={src} style={{ ...layer, clipPath: `inset(${(SEAM - 2) * k}px 0 0 0)` }} />
        <div style={{ ...layer, clipPath: `inset(0 0 ${(CH - SEAM) * k}px 0)`, transform: `translateY(${lift}px)` }}>
          <Img src={src} style={layer} />
          {showMouth && <Img src={staticFile(`character/pixel_mouths/${pose}/${viseme}.png`)} style={layer} />}
        </div>
      </div>
    </div>
  );
};

// ─── acting: one pose per voiceover line ─────────────────────────────────────
/** A pose cue: switch to `pose` when voiceover segment `from` starts. */
export type PoseCue<Seg extends string = string> = { from: Seg; pose: Pose; flip?: boolean };
type Segs = Record<string, { start: number }>;

/** Frames spent in the neutral in-between pose on a switch (when `inbetween` is on). */
const THROUGH = 2;

/**
 * Which pose is on at `frame`, and for how long (drives the squash/overshoot pop).
 * The new pose lands `lead` frames before the line starts, so the body moves just ahead of the words.
 * inbetween: pass through "idle" for 2 frames on each switch, so the arms read as swinging
 * through rest instead of teleporting (skipped when either side is already idle).
 */
export const poseAt = (script: readonly PoseCue[], segs: Segs, frame: number, fps: number, lead = 3, inbetween = false) => {
  let cur: { pose: Pose; flip?: boolean; at: number } = { pose: script[0]?.pose ?? "idle", flip: script[0]?.flip, at: -99 };
  for (const [i, cue] of script.entries()) {
    const at = Math.round(segs[cue.from].start * fps) - lead;
    const prev = i > 0 ? script[i - 1].pose : null;
    const through = inbetween && prev !== null && prev !== cue.pose && prev !== "idle" && cue.pose !== "idle";
    if (through && frame >= at - THROUGH && frame < at) return { pose: "idle" as Pose, flip: cue.flip, sincePose: 99 };
    if (frame >= at) cur = { pose: cue.pose, flip: cue.flip, at };
  }
  return { pose: cur.pose, flip: cur.flip, sincePose: frame - cur.at };
};

/**
 * Minimum hold for mouth shapes: a shape must stay at least `min` frames before the next one
 * shows (like animating the mouth "on twos"), so the tiny mouth reads as rhythm, not flicker.
 * Cached per track.
 */
const heldCache = new WeakMap<Lipsync, string[]>();
export const heldVisemes = (track: Lipsync, min = 2) => {
  const hit = heldCache.get(track);
  if (hit) return hit;
  const out: string[] = [];
  let cur = track.visemes[0] ?? "rest";
  let held = 0;
  for (const v of track.visemes) {
    if (v !== cur && held >= min) {
      cur = v;
      held = 0;
    }
    out.push(cur);
    held++;
  }
  heldCache.set(track, out);
  return out;
};

/**
 * The character acting a voiceover: pose from `script`, mouth + nod from a lipsync.py track.
 * `offset` = frames to subtract when the voiceover starts later than frame 0 of the composition.
 */
export const CharacterActor: React.FC<{
  script: readonly PoseCue[];
  segs: Segs;
  lipsync: Lipsync;
  frame: number;
  offset?: number;
  inbetween?: boolean;
  style?: CharStyle;
  height?: number;
  css?: React.CSSProperties;
}> = ({ script, segs, lipsync, frame, offset = 0, inbetween = true, style = "pixel", height, css }) => {
  const t = frame - offset;
  const { pose, flip, sincePose } = poseAt(script, segs, t, lipsync.fps, 3, inbetween);
  const s = speechAt(lipsync, t);
  const viseme = (heldVisemes(lipsync)[t] ?? "rest") as Viseme;
  return (
    <Character pose={pose} flip={flip} sincePose={sincePose} frame={frame} viseme={viseme} nod={s.nod} style={style} height={height} css={css} />
  );
};

// ─── preview: both styles side by side, walk-in, then every pose ─────────────
const { fontFamily: SANS } = loadInter("normal", { weights: ["600"], subsets: ["latin"] });
const HOLD = 24;
const INTRO = 18;
export const CHAR_PREVIEW_DURATION = INTRO + POSES.length * HOLD + 20;

export const CharacterPreview: React.FC = () => {
  const frame = useCurrentFrame();
  const i = Math.min(POSES.length - 1, Math.max(0, Math.floor((frame - INTRO) / HOLD)));
  const pose: Pose = frame < INTRO ? "idle" : POSES[i];
  const since = frame < INTRO ? 99 : (frame - INTRO) % HOLD;
  const enter = interpolate(frame, [0, INTRO], [-420, 0], { ...clamp, easing: Easing.bezier(0.16, 1, 0.3, 1) });
  const label = (text: string, x: number) => (
    <div style={{ position: "absolute", left: x, top: 250, width: 540, textAlign: "center", fontFamily: SANS, fontWeight: 600, fontSize: 40, color: "#8C8C92" }}>{text}</div>
  );
  return (
    <AbsoluteFill style={{ background: "#0B0B0C" }}>
      <AbsoluteFill style={{ backgroundImage: "linear-gradient(rgba(255,255,255,0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.05) 1px, transparent 1px)", backgroundSize: "54px 54px", opacity: 0.6 }} />
      {label("Illustrated", 0)}
      {label("Pixel", 540)}
      <Character style="illustrated" pose={pose} height={1000} sincePose={since} frame={frame} css={{ left: enter - 212 + 270 - 482 / 2 + 0, top: 440 }} />
      <Character style="pixel" pose={pose} height={1000} sincePose={since} frame={frame} css={{ left: enter + 540 - 212 + 270 - 482 / 2 + 0, top: 440 }} />
      <div style={{ position: "absolute", left: 0, width: 1080, top: 1560, textAlign: "center", fontFamily: SANS, fontWeight: 600, fontSize: 56, color: "#F4F4F2" }}>
        {pose.replace("_", " ")}
      </div>
    </AbsoluteFill>
  );
};
