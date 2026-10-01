// Light-theme thumbnail: the NBC hook in heavy type, the three product marks as the cast.
// Everything sits inside the 3:4 profile-grid crop (y 240–1680).
import React from "react";
import { AbsoluteFill } from "remotion";
import { DOT_COLORS, DotChar, GrokChar, INK, Jolly, LIME, Logo, PAPER } from "./marks";

export const Cover: React.FC = () => (
  <AbsoluteFill style={{ background: PAPER }}>
    <div style={{ position: "absolute", left: 70, top: 300, display: "flex", alignItems: "center", gap: 26 }}>
      <Logo name="xai" size={50} color={INK} />
      <Logo name="meta" size={50} color={INK} />
      <Logo name="openai" size={50} color={INK} />
      <div style={{ fontFamily: "'Silkscreen', monospace", fontSize: 28, background: INK, color: PAPER, padding: "6px 14px", marginLeft: 8 }}>3 AI AGENTS · 49 DAYS</div>
    </div>
    <div style={{ position: "absolute", left: 62, top: 400, width: 960, fontFamily: "'Archivo Black', sans-serif", color: INK, fontSize: 138, lineHeight: 0.92, letterSpacing: -5 }}>
      IT’S CUTE.<br />IT’S CUDDLY.<br />
      <span style={{ background: LIME, padding: "0 16px", boxDecorationBreak: "clone", WebkitBoxDecorationBreak: "clone" }}>IT WANTS<br />YOUR DATA.</span>
    </div>
    <div style={{ position: "absolute", left: 70, top: 1050, width: 940, display: "flex", alignItems: "flex-end", justifyContent: "space-between" }}>
      <GrokChar size={200} frame={0} />
      <Jolly size={390} frame={20} wave={1} />
      <DotChar size={220} frame={0} color={DOT_COLORS[0]} />
    </div>
    <div style={{ position: "absolute", left: 70, top: 1560, fontFamily: "'Jersey 10', sans-serif", fontSize: 64, color: INK }}>
      YOUR NEXT COWORKER ISN’T HUMAN.
    </div>
  </AbsoluteFill>
);
