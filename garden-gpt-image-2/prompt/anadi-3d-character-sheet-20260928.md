Attach reference: character/character_sheet.png (and/or avatar/final/source_ai_portrait_full.jpg for the face)

{
  "type": "3D character turnaround sheet",
  "goal": "Turn the man in the reference image into a stylized 3D collectible-figure character, and lay him out on one sheet that can be fed straight into an image-to-3D tool (Meshy) and 3D printed",
  "character": {
    "name": "Anadi",
    "concept": "Chill, confident AI builder and creator. Slightly smug half-smile.",
    "art_style": "Stylized 3D caricature like a premium vinyl/clay collectible figure: slightly big head (about 1:5 head-to-body), exaggerated but recognizable features, soft sculpted forms, matte painted-resin surface, soft studio lighting, Pixar/Laika-inspired",
    "likeness": "Keep his face recognizable from the reference: beard shape, nose, eyebrows, long dark hair falling out of the hood",
    "outfit": "Black zip hoodie with the hood up and white drawstrings, plain black tee, round dark sunglasses, white slim-fit trousers, chunky white sneakers"
  },
  "sections": {
    "hero": "Large front-facing full-body A-pose in the centre, arms slightly away from the body, feet flat and shoulder-width apart, standing on a small round base",
    "three_view": ["front", "left side", "back", "3/4 view"], all full-body, same scale, lined up on the same ground line,
    "expression_grid": ["neutral", "smirk", "laughing", "mind blown", "facepalm", "thinking", "surprised", "sunglasses lowered with a raised eyebrow"],
    "pose_strip": ["arms crossed", "pointing up", "holding a laptop", "shrug", "wave", "thumbs up"],
    "details": ["close-up of the sunglasses", "hoodie drawstring and zip", "sneaker from the side", "hand"],
    "color_palette": "ink black #0A0A0C, paper white #F4F4F2, skin tone swatch, beard/hair dark brown, accent lime #D4FF3A (only as a small detail, e.g. sneaker tab or hoodie tag)"
  },
  "layout": {
    "background": "Clean off-white paper background with a faint grid, like an animation studio model sheet",
    "grid": "Thin divider lines and small section labels; a short notes column on the right (name, height, materials)"
  },
  "aspect_ratio": "16:9",
  "constraints": {
    "must_keep": [
      "Same character, same proportions, same outfit in every view",
      "Turnaround views are clean and unobstructed, with no overlapping limbs (so they work for image-to-3D)",
      "Solid, printable shapes: no thin floating parts, drawstrings attached to the body"
    ],
    "avoid": [
      "Realistic photo look", "anime or 2D flat style", "the views looking like different people",
      "cast shadows covering the figure", "cluttered background", "text over the character"
    ]
  }
}
