// The story's "characters": product marks in colour (Grok glyph tile, Jolly, Dots) + brand logos in mono.
// Jolly and the Dots are illustrations drawn from the press descriptions (NBC: Jolly is "cream-colored,
// beady black eyes, an upward smile"; TechCrunch: Dots are "bubbly", brightly coloured orbs) — not official art.
import React from "react";
import { LOGOS, LogoName } from "./logos";

export const INK = "#0A0A0C";
export const PAPER = "#F4F4F2";
export const LIME = "#D4FF3A";
export const DOT_COLORS = ["#FF6B5B", "#4C8DFF", "#FFC83D", "#B57BFF", "#34D399"];

export const Logo: React.FC<{ name: LogoName; size: number; color: string; style?: React.CSSProperties }> = ({ name, size, color, style }) => {
  const l = LOGOS[name];
  const [, , w, h] = l.vb.split(" ").map(Number);
  return (
    <svg viewBox={l.vb} width={(size * w) / h} height={size} style={{ color, display: "block", ...style }}>
      {l.paths.map((d, i) => <path key={i} d={d} fill="currentColor" fillRule="evenodd" />)}
    </svg>
  );
};

/** Grok Bot: the Grok glyph on its own black tile (its real colours), with a "working" ring. */
export const GrokChar: React.FC<{ size: number; frame: number; working?: boolean; style?: React.CSSProperties }> = ({ size, frame, working, style }) => {
  const bob = Math.sin(frame / 9) * size * 0.02;
  const a = (frame * 9) % 360;
  return (
    <div style={{ width: size, height: size, position: "relative", transform: `translateY(${bob}px)`, ...style }}>
      <svg viewBox="0 0 100 100" width={size} height={size} style={{ position: "absolute", inset: 0 }}>
        <rect x="6" y="6" width="88" height="88" rx="22" fill="#000" stroke="#2A2A2E" strokeWidth="1.5" />
        {working && (
          <circle cx="50" cy="50" r="47" fill="none" stroke={LIME} strokeWidth="2.5" strokeDasharray="40 255"
            transform={`rotate(${a} 50 50)`} strokeLinecap="round" />
        )}
      </svg>
      <div style={{ position: "absolute", inset: size * 0.24 }}>
        <Logo name="grok" size={size * 0.52} color="#FFFFFF" />
      </div>
    </div>
  );
};

/** Jolly, Muse's default avatar: a cream plush with beady eyes and an upward smile. */
export const Jolly: React.FC<{ size: number; frame: number; wave?: number; style?: React.CSSProperties }> = ({ size, frame, wave = 0, style }) => {
  const squash = 1 + Math.sin(frame / 7) * 0.025;
  const blink = (frame + 40) % 96 < 4 ? 0.15 : 1;
  const armA = 14 + wave * (34 + Math.sin(frame / 3) * 18);
  return (
    <svg viewBox="0 0 200 220" width={size} height={size * 1.1} style={{ display: "block", overflow: "visible", ...style }}>
      <ellipse cx="100" cy="212" rx="62" ry="7" fill="#000" opacity="0.12" />
      <g transform={`translate(100 210) scale(${1 / squash} ${squash}) translate(-100 -210)`}>
        {/* ears */}
        <ellipse cx="62" cy="42" rx="18" ry="22" fill="#EFE3CB" stroke="#D9C9A8" strokeWidth="2" />
        <ellipse cx="138" cy="42" rx="18" ry="22" fill="#EFE3CB" stroke="#D9C9A8" strokeWidth="2" />
        {/* body */}
        <path d="M100 30 C 160 30 178 80 176 130 C 174 185 145 210 100 210 C 55 210 26 185 24 130 C 22 80 40 30 100 30 Z"
          fill="#F3E9D4" stroke="#D9C9A8" strokeWidth="2.5" />
        <ellipse cx="100" cy="160" rx="44" ry="34" fill="#FBF5E8" />
        {/* arms (in front, sticking out at the sides) */}
        <g transform={`rotate(${armA} 40 124)`}><ellipse cx="14" cy="124" rx="24" ry="15" fill="#EFE3CB" stroke="#D9C9A8" strokeWidth="2.5" /></g>
        <g transform="rotate(-14 160 128)"><ellipse cx="186" cy="132" rx="24" ry="15" fill="#EFE3CB" stroke="#D9C9A8" strokeWidth="2.5" /></g>
        {/* face */}
        <g transform={`translate(0 ${100 * (1 - blink)}) scale(1 ${blink})`} style={{ transformOrigin: "100px 96px" }}>
          <circle cx="78" cy="96" r="7.5" fill="#121212" />
          <circle cx="122" cy="96" r="7.5" fill="#121212" />
          <circle cx="80.5" cy="93.5" r="2.2" fill="#fff" />
          <circle cx="124.5" cy="93.5" r="2.2" fill="#fff" />
        </g>
        <path d="M86 114 Q 100 128 114 114" fill="none" stroke="#121212" strokeWidth="4" strokeLinecap="round" />
        <ellipse cx="64" cy="114" rx="9" ry="5" fill="#F5B9A8" opacity="0.6" />
        <ellipse cx="136" cy="114" rx="9" ry="5" fill="#F5B9A8" opacity="0.6" />
      </g>
    </svg>
  );
};

/** A Dot: a glossy, brightly coloured bubble with a face. */
export const DotChar: React.FC<{ size: number; frame: number; color: string; seed?: number; style?: React.CSSProperties }> = ({ size, frame, color, seed = 0, style }) => {
  const f = frame + seed * 17 + 50;
  const bob = Math.sin(f / 8) * 4;
  const blink = f % 110 < 4 ? 0.12 : 1;
  const id = `dg${color.slice(1)}${seed}`;
  return (
    <svg viewBox="0 0 100 108" width={size} height={size * 1.08} style={{ display: "block", overflow: "visible", ...style }}>
      <defs>
        <radialGradient id={id} cx="35%" cy="30%" r="75%">
          <stop offset="0%" stopColor="#ffffff" stopOpacity="0.85" />
          <stop offset="22%" stopColor={color} />
          <stop offset="100%" stopColor={color} stopOpacity="1" />
        </radialGradient>
      </defs>
      <ellipse cx="50" cy="104" rx="26" ry="3.5" fill="#000" opacity="0.18" />
      <g transform={`translate(0 ${bob})`}>
        <circle cx="50" cy="50" r="44" fill={`url(#${id})`} />
        <circle cx="50" cy="50" r="44" fill="none" stroke="#000" strokeOpacity="0.12" strokeWidth="1.5" />
        <ellipse cx="34" cy="28" rx="11" ry="6" fill="#fff" opacity="0.55" transform="rotate(-25 34 28)" />
        <g transform={`translate(0 ${52 * (1 - blink)}) scale(1 ${blink})`}>
          <ellipse cx="38" cy="52" rx="5" ry="7" fill="#111" />
          <ellipse cx="62" cy="52" rx="5" ry="7" fill="#111" />
        </g>
        <path d="M43 66 Q 50 72 57 66" fill="none" stroke="#111" strokeWidth="3" strokeLinecap="round" />
      </g>
    </svg>
  );
};

/** A generic, boxy, unfriendly robot for the "you won't hand it to a robot" beat. */
export const Robot: React.FC<{ size: number; frame: number; color?: string }> = ({ size, frame, color = "#8A8A90" }) => {
  const eye = frame % 40 < 20 ? "#FF4D4D" : "#B83232";
  return (
    <svg viewBox="0 0 100 120" width={size} height={size * 1.2} style={{ display: "block" }}>
      <line x1="50" y1="4" x2="50" y2="18" stroke={color} strokeWidth="3" />
      <circle cx="50" cy="4" r="4" fill={eye} />
      <rect x="18" y="18" width="64" height="46" fill={color} stroke="#3A3A40" strokeWidth="2" />
      <rect x="28" y="32" width="14" height="8" fill={eye} />
      <rect x="58" y="32" width="14" height="8" fill={eye} />
      <rect x="34" y="50" width="32" height="4" fill="#3A3A40" />
      <rect x="24" y="68" width="52" height="40" fill={color} stroke="#3A3A40" strokeWidth="2" />
      <rect x="8" y="72" width="12" height="30" fill={color} stroke="#3A3A40" strokeWidth="2" />
      <rect x="80" y="72" width="12" height="30" fill={color} stroke="#3A3A40" strokeWidth="2" />
    </svg>
  );
};

export const Check: React.FC<{ size: number; color: string; p?: number }> = ({ size, color, p = 1 }) => (
  <svg viewBox="0 0 24 24" width={size} height={size} style={{ display: "block" }}>
    <path d="M4 12.5 L10 18 L20 6" fill="none" stroke={color} strokeWidth="3.4" strokeLinecap="square"
      strokeDasharray="30" strokeDashoffset={30 * (1 - p)} />
  </svg>
);
