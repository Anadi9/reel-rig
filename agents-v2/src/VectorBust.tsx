// Head-to-shoulders redraw of the vector Anadi character (hood down, swept dark hair, octagon shades,
// full beard, black hoodie with white drawstrings, lime rim light on the right) for the narrator slot.
// A look-alike drawn from the rig's renders — the real rig lives in remotion/src/vector-char/ on the Mac.
// Mouth shapes follow the avatar/lipsync.py visemes: rest | a1 a2 a3 (open) | e1 e2 (wide) | o1 o2 (round).
import React from "react";

const SKIN = "#D9A06E", SKIN_SH = "#C38957", HAIR = "#1F1A19", HAIR_HI = "#3A3230", BEARD = "#241B18";
const HOOD = "#23242C", HOOD_SH = "#1A1B21", RIM = "#D4FF3A", FRAME = "#AEB6C4", LENS = "#121318", LIP = "#B87560";

const oct = (cx: number, cy: number, w = 68, h = 44, c = 12) =>
  [[cx - w / 2 + c, cy - h / 2], [cx + w / 2 - c, cy - h / 2], [cx + w / 2, cy - h / 2 + c], [cx + w / 2, cy + h / 2 - c],
   [cx + w / 2 - c, cy + h / 2], [cx - w / 2 + c, cy + h / 2], [cx - w / 2, cy + h / 2 - c], [cx - w / 2, cy - h / 2 + c]]
    .map((p) => p.join(",")).join(" ");

const Mouth: React.FC<{ v: string }> = ({ v }) => {
  if (v === "rest") return <path d="M184 266 Q200 274 216 266" fill="none" stroke={LIP} strokeWidth="6" strokeLinecap="round" />;
  const open: Record<string, [number, number]> = { a1: [15, 6], a2: [17, 10], a3: [18, 14], e1: [21, 6], e2: [23, 8], o1: [10, 10], o2: [8, 12] };
  const [rx, ry] = open[v] ?? [15, 7];
  return (
    <g>
      <ellipse cx="200" cy="268" rx={rx + 4} ry={ry + 4} fill={LIP} />
      <ellipse cx="200" cy="268" rx={rx} ry={ry} fill="#3A1712" />
      {ry > 7 && v[0] !== "o" && <rect x={200 - rx * 0.7} y={268 - ry} width={rx * 1.4} height={Math.min(5, ry * 0.4)} fill="#F2EEE8" rx="1.5" />}
    </g>
  );
};

export const VectorBust: React.FC<{ width: number; viseme: string; brow: boolean; tilt?: number; style?: React.CSSProperties }> = ({ width, viseme, brow, tilt = 0, style }) => {
  const by = brow ? -7 : 0;
  return (
    <svg viewBox="0 0 400 460" width={width} height={(width * 460) / 400} style={{ display: "block", overflow: "visible", ...style }}>
      {/* torso + hood bunched around the neck */}
      <path d="M8 470 C 14 400 40 360 110 340 L 290 340 C 360 360 386 400 392 470 Z" fill={HOOD} />
      <path d="M290 340 C 360 360 386 400 392 470" fill="none" stroke={RIM} strokeWidth="4" />
      <path d="M8 470 C 14 400 40 360 110 340" fill="none" stroke="#0B0B0D" strokeWidth="3" />
      <path d="M118 356 C 130 316 170 332 200 336 C 232 332 272 316 284 356 C 260 372 230 380 200 380 C 170 380 142 372 118 352 Z" fill={HOOD_SH} />
      {/* drawstrings */}
      <path d="M184 368 L 180 452" stroke="#E6E6EA" strokeWidth="6" strokeLinecap="round" />
      <path d="M216 368 L 220 452" stroke="#E6E6EA" strokeWidth="6" strokeLinecap="round" />
      <rect x="175" y="446" width="10" height="14" fill="#9BA1AC" /><rect x="215" y="446" width="10" height="14" fill="#9BA1AC" />

      <g transform={`rotate(${tilt} 200 330)`}>
        {/* neck */}
        <path d="M174 280 L 174 362 C 186 372 214 372 226 362 L 226 280 Z" fill={SKIN_SH} />
        {/* ears */}
        <ellipse cx="111" cy="192" rx="12" ry="20" fill={SKIN} /><ellipse cx="113" cy="194" rx="6" ry="11" fill={SKIN_SH} />
        <ellipse cx="289" cy="192" rx="12" ry="20" fill={SKIN} /><ellipse cx="287" cy="194" rx="6" ry="11" fill={SKIN_SH} />
        <path d="M298 178 C 303 188 302 202 294 210" fill="none" stroke={RIM} strokeWidth="3" />
        {/* face */}
        <path d="M114 150 C 114 112 146 96 200 96 C 254 96 286 112 286 150 L 288 220 C 286 284 246 316 200 316 C 154 316 114 284 112 220 Z" fill={SKIN} />
        {/* beard (cheeks, jaw, moustache) */}
        <path d="M112 196 C 110 276 150 322 200 324 C 250 322 290 276 288 196 L 276 198 C 274 230 258 242 242 240 C 228 236 214 234 200 236 C 186 234 172 236 158 240 C 142 242 126 230 124 198 Z" fill={BEARD} />
        <path d="M156 292 C 176 306 224 306 244 292" fill="none" stroke="#352925" strokeWidth="3" opacity="0.7" />
        <Mouth v={viseme} />
        {/* nose */}
        <path d="M201 186 C 197 204 190 218 192 226 C 198 232 208 231 212 226" fill="none" stroke={SKIN_SH} strokeWidth="5" strokeLinecap="round" />
        {/* hair: swept quiff, lime rim on the right */}
        <path d="M110 168 C 98 104 120 60 158 44 C 176 20 222 10 250 16 C 282 22 304 50 304 92 C 304 120 300 144 294 168 L 284 132 C 278 114 254 116 234 110 C 204 102 158 106 134 120 C 122 128 116 146 114 170 Z" fill={HAIR} />
        <path d="M200 22 C 230 2 286 8 300 42 C 280 24 244 20 214 30 Z" fill={HAIR} />
        <path d="M146 64 C 180 44 232 40 262 62" fill="none" stroke={HAIR_HI} strokeWidth="4" strokeLinecap="round" />
        <path d="M188 46 C 214 58 222 80 214 100" fill="none" stroke={HAIR_HI} strokeWidth="3.5" strokeLinecap="round" />
        <path d="M226 16 C 252 4 286 14 298 40 C 306 70 304 110 294 166" fill="none" stroke={RIM} strokeWidth="4.5" strokeLinecap="round" />
        {/* brows */}
        <g transform={`translate(0 ${by})`}>
          <path d="M126 150 C 142 134 168 130 188 140 L 186 152 C 166 147 144 149 129 161 Z" fill="#191514" />
          <path d="M274 150 C 258 134 232 130 212 140 L 214 152 C 234 147 256 149 271 161 Z" fill="#191514" />
        </g>
        {/* octagon shades */}
        <path d="M122 178 L 110 184 M278 178 L 290 184" stroke={FRAME} strokeWidth="4.5" />
        <path d="M192 178 Q 200 172 208 178" fill="none" stroke={FRAME} strokeWidth="4.5" />
        <polygon points={oct(158, 184)} fill={LENS} stroke={FRAME} strokeWidth="5" strokeLinejoin="round" />
        <polygon points={oct(242, 184)} fill={LENS} stroke={FRAME} strokeWidth="5" strokeLinejoin="round" />
        <path d="M144 196 L 158 172 M154 198 L 166 178 M228 196 L 242 172 M238 198 L 250 178" stroke="#3A3E47" strokeWidth="4" strokeLinecap="round" />
      </g>
    </svg>
  );
};
