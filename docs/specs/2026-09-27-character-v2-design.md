# Character v2: more poses, head rig, word-timed lip-sync, livelier motion

Date: 2026-09-27 · Status: draft, waiting for Anadi's review

## Why

The full-body pixel character (`character/`, `remotion/src/character/`) is going into many more
@the.anadi reels. Anadi wants three things: **polish** (clean edges, no feet sliding, no awkward
poses), **range** (more poses and reactions) and **life** (better talking, a head that moves on
its own, walking in and out, smoother pose changes, idle motion).

## Decisions already made

- Full-body only. Size and placement stay as in `REEL_NOTES.md`: 490px tall, centred, pill under
  the feet, inside the safe zone.
- Pixel style (2px cells, shared palette, selective outline) and the lime right-edge rim stay.
- New art comes from Anadi's two new sheets, saved as:
  - `character/sheets/sheet4_full_8x3.webp`: 24 full-body poses, all used
  - `character/sheets/sheet3_mixed_6x4.webp`: mostly cut off at the thigh; only its 3 full-body
    figures are used
- Merge rule: where an old pose and a new one show the same action, the **new one wins and takes
  the old name**. Old poses with no new equivalent are kept. Anadi approves an old-vs-new board
  before anything is replaced.
- The head gets its own layer, split out automatically in the build (approach A). Poses with a
  hand on or around the face keep today's upper-body nod.
- Existing reels keep compiling. When re-rendered they pick up the new art and motion. There is no
  frozen "v1 mode".

## Pose list

`talks` = can lip-sync · `head` = `split` (own layer) or `fixed` (upper-body nod only) ·
`stance` = `stand` (mouth aligned to (270,121)) or `walk` / `sit` / `crouch` (feet on the
baseline only, not mouth-aligned). "review" means the review board decides.

**Kept from v1 (sheets 1–2), unchanged art:**
idle, talk, point_up, hold_paper, point_down, wave (all stand · talks · split), and
mind_blown (stand · no talk, since the "O" mouth is drawn in · fixed).

**Replaced by sheet 4 art (same names):**

| name | cell | talks | head | stance |
|---|---|---|---|---|
| laptop | r1c1 | yes | split | stand |
| phone | r1c2 | yes | split | stand |
| facepalm | r1c3 | yes | fixed | stand |
| thumbs_up | r1c4 | yes | split | stand |
| shrug | r1c6 | yes | split | stand |

**New from sheet 4 (8×3):**

| name | cell | what | talks | head | stance |
|---|---|---|---|---|---|
| arms_crossed | r1c5 | arms crossed | yes | split | stand |
| point_side | r1c7 | points off to the right, looking there | review | split | stand |
| lean | r1c8 | hands in pockets, legs crossed | yes | split | stand |
| walk_a | r2c1 | walking, facing left | no | split | walk |
| coffee | r2c2 | sipping coffee | no | fixed | stand |
| laptop_look | r2c3 | laptop, looking down at it | yes | split | stand |
| hands_up | r2c4 | both hands raised by the head (gesture to confirm on the board) | yes | review | stand |
| point_up_both | r2c5 | both index fingers up, looking up | review | split | stand |
| phone_call | r2c6 | phone at ear | yes | fixed | stand |
| relaxed | r2c7 | hands behind head | yes | fixed | stand |
| lean_crossed | r2c8 | arms and legs crossed | yes | split | stand |
| jog | r3c1 | mid-stride, fists up | no | split | walk |
| crouch_think | r3c2 | crouching, hand on chin | no | fixed | crouch |
| tablet | r3c3 | holding a tablet | yes | split | stand |
| finger_guns | r3c4 | double finger-guns | yes | split | stand |
| celebrate | r3c5 | both fists raised | yes | split | stand |
| present | r3c6 | open hand presenting to the side | yes | split | stand |
| idle_pockets | r3c7 | hands in pockets | yes | split | stand |
| back | r3c8 | back view, walking away | no | split | walk |

**New from sheet 3 (6×4, full-body figures only):**

| name | cell | what | talks | head | stance |
|---|---|---|---|---|---|
| sit | r2c1 | sitting, forearms on knees | yes | split | sit |
| walk_b | r3c6 | walking, facing right | no | split | walk |
| sit_laptop | r4c3 | cross-legged with a laptop | yes | split | sit |

That's 34 poses in total. `talk` and `present` are close; both stay and the board shows them next
to each other. The walk cycle uses walk_a and walk_b, one of them mirrored so both face the same
way; the board confirms they read as two steps.

## Part 1: Pose build pipeline (`character/build_character.py`)

1. **Manifest.** `character/poses.yaml` replaces the hard-coded `SHEETS`, `POSES` and `MOUTH_RAW`.
   Each entry: `name, sheet, grid [cols, rows], cell [row, col], talks, head, stance`, plus
   optional hand-set `mouth [x, y]`, `neck [x, y]` and `lenses [[x, y, r], [x, y, r]]` that
   override the automatic values. `poses.json` stays as a generated summary for Remotion and
   `build_mouths.py`.
2. **Cut-outs by grid cell.** Each sheet is split into its grid cells. Inside a cell the largest
   foreground piece is the figure, plus any pieces that touch it (hands and props). The existing
   halo and fringe cleanup is kept. Jagged trouser edges get an extra contour smooth limited to
   light, low-colour edge pixels.
3. **Scale by head size.** Every pose is scaled so its head width (hood width at the lens row)
   matches `idle`'s, with the feet on `BASE = 548`. `stand` poses are then shifted sideways and
   up or down so the mouth lands on (270, 121). The build logs every shift and fails if a
   standing pose's feet would move more than 4px from the baseline. `walk`, `sit` and `crouch`
   poses keep the head scale, are centred on the head, and are not mouth-aligned.
4. **Automatic landmarks.**
   - mouth: centre of the skin gap between moustache and beard, below the lenses
   - neck: narrowest point of the silhouette between the chin and the shoulders
   - lenses: two dark blobs inside the face

   All three are drawn on `landmarks_board.png`. Bad detections are fixed in the manifest.
5. **Old-vs-new board.** `replace_board.png` shows the 5 replaced poses (v1 vs v2 art at the same
   scale), and `talk` next to `present`. Anadi approves it before the new art is synced.
6. The output layout is unchanged: `illustrated/`, `pixel/<pose>.png` (whole sprite, as today),
   `pixel_mouths/`, plus the Part 2 layers. `build.sh` still runs everything and syncs to
   `remotion/public/character/`.

## Part 2: Head layer (new `character/build_heads.py`)

For every `head: split` pose:

- **`pixel_layers/<pose>/body.png`**: the pose without the head. The cut is a curve through the
  neck point along the collar. The face, beard and hood crown go with the head, and the hood sides
  resting on the shoulders stay on the body. The area behind the head is filled with the
  hood-lining colour, so a tilt only reveals dark hoodie.
- **`pixel_layers/<pose>/head.png`**: an atlas of 5 angles (−4°, −2°, 0°, +2°, +4°) × 9 mouth
  states (`rest`, a1, a2, a3, e1, e2, o1, o2, plus `m`, a sealed closed mouth for m/b/p). Each
  frame is rotated at full resolution about the neck point, then pixelated again on the same 2px
  grid and shared palette, so tilts stay crisp. Open-mouth frames (a2, a3, o2) have the jaw drop
  baked in: beard cells below the mouth shift down 1 cell.
- **The neck pivot and the atlas layout** are written to `poses.json`.

`head: fixed` poses keep the whole sprite plus the mouth overlays from `pixel_mouths/`. This is
today's system, with the `m` shape added.

`neck_board.png` shows every split pose at −4°, 0° and +4° next to the flat original. Any pose
whose cut looks wrong is switched to `head: fixed` in the manifest.

## Part 3: Lip-sync and head acting (`avatar/lipsync.py` v2)

Usage: `lipsync.py <vo.wav> <out.ts> [--script cfg/<reel>.json] [fps]`

1. **Words.** With `--script`, the exact script text is aligned to the audio with faster-whisper
   word timestamps. Without it, Whisper's own transcript is used.
2. **Sounds.** Each word is turned into phonemes with espeak-ng (the phonemizer Piper already
   uses). The phonemes are spread across the word's time, with vowels weighted 2× over
   consonants.
3. **Mouth shapes.**
   - m, b, p → `m`
   - f, v → a1
   - open vowels (ɑ æ ʌ a aɪ aʊ) → a-family
   - front vowels (i ɪ e ɛ eɪ) and s, z → e-family
   - rounded (u ʊ o ɔ oʊ w) → o-family
   - other consonants → the previous vowel's family, one step less open
   - silence → rest

   Loudness picks the step inside a family (a1, a2 or a3). The existing hold of at least 2 frames
   and the 3-frame majority filter stay.
4. **Head acting.**
   - `bob`: stressed-syllable onsets, as today
   - `tilt`: −1, 0 or +1, eased over 4 frames and held through any line ending in "?"; the side
     alternates per question
   - `beat`: a 1-cell dip at commas
   - `turn`: −1, 0 or +1; set per pose at render time (Part 4), not in the track
5. **Output.** Same `LIPSYNC` shape as today (`viseme`, `bob`, `brow`) plus `tilt` and `beat`
   arrays, so old tracks still load and new fields default to 0. If Whisper or espeak-ng fails, it
   prints a warning and falls back to the current loudness method.
6. **Run scripts.** `run_model_drift_reel.sh` and future run scripts pass `--script`.

Check: `LipsyncCompare`, a composition showing a head-only close-up with the old and new track
side by side on the model-drift voiceover.

## Part 4: Motion runtime (`remotion/src/character/Character.tsx`)

- **Pose union.** `POSES` and `Pose` are generated from `poses.json`, so new poses need no code
  change.
- **Rendering.**
  - Split poses draw `body.png`, then one frame of the head atlas at the neck pivot.
  - Fixed poses draw today's two-part sprite with mouth overlays.
  - Every offset is a whole number of 2px cells.
- **Head motion.**
  - nod = `bob` or `beat`, 1 cell down
  - tilt = the atlas angle column: ±2° for a light tilt, ±4° for a held question
  - turn = 1 cell sideways plus `scaleX(0.97)` on the head. It follows the pose: `point_side`,
    `present` and a flipped `talk` turn toward the pointing side.
  - `PoseCue` gains an optional `head: { tilt?: -2|-1|0|1|2, turn?: -1|0|1 }` to force it for a
    line.
- **Pose changes.** A new `transition` prop:
  - `"dither"` (default): a 3-frame 4×4 ordered-dither dissolve between the two sprites, then a
    1-cell settle, feet pinned
  - `"pop"`: today's idle flash plus squash and overshoot
  - `"cut"`: instant switch

  `inbetween={false}` keeps working as an alias for `"cut"`.
- **Walk in and out.** `enter` and `exit` props, `{ side: "left" | "right", frames: number }`.
  - The character slides from off-screen to its place, switching between walk_a and walk_b
    every 6 frames with a 1-cell bob per step.
  - It is mirrored so it faces the direction of travel, then dissolves into the first cue's pose.
  - `exit` is the same in reverse from `frames` before the end.
  - Known limit: with only 2 drawings it is a stylised 2-step walk.
- **Idle life** (`idleLife`, default on):
  - The breathing stays.
  - Weight shift: the upper body (or head and body layers together) moves 1 cell sideways and
    back every ~3 s. The phase is set per reel so reels don't look identical.
  - Shades glint: a 3-frame diagonal highlight across both lenses, at most every 4–6 s, only
    during holds over 2 s. It needs the lens landmarks.
- **Compatibility.** Every existing prop and pose name keeps working. `model-drift` compiles and
  renders with no code change.

## Testing and acceptance

1. `build.sh` runs cleanly and writes `character_sheet.png` (all 34 poses), `landmarks_board.png`,
   `replace_board.png`, `neck_board.png` and `mouth_board.png`. Anadi signs off `replace_board`
   before the new art is synced.
2. No standing pose moves its feet more than 4px on a switch (checked by the build).
3. `npx tsc --noEmit` passes in `remotion/`.
4. `CharacterTalkDemo` is updated to walk in, act every talking pose over the model-drift
   voiceover, show idle life and walk out. Anadi reviews the render.
5. `LipsyncCompare` render: m/b/p show a closed mouth and "oo" shows a round one, judged by Anadi.
6. `./run_model_drift_reel.sh` re-renders with the v2 character. Checked frames stay inside the
   safe zones (captions y ≥ 280, pill bottom ≤ 1600, nothing at x > 940 in y 1200–1600).
7. Docs: `character/README.md` is rewritten for v2 (the handle becomes @the.anadi, the size advice
   points to REEL_NOTES' 490px). `REEL_NOTES.md` gets a Character v2 entry.

## Out of scope

Half-body or close-up framing, new art generation, 3/4 head turns, a smooth walk cycle (needs more
walk drawings), eyebrow motion (hidden by the shades), and changes to reels other than the
model-drift test render.
