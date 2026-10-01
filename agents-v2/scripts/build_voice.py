#!/usr/bin/env python3
"""Piper voiceover for the agents v2 reel: one take per script line, joined with the
script's pauses. Writes public/vo.wav and src/timing.json (line + caption-chunk times, seconds).

Chunk times inside a line are split by spoken character count, which tracks Piper's pace
closely enough for 2-line captions. Run from agents-v2/: python3 scripts/build_voice.py
"""
import io, json, os, re, sys, wave
from piper import PiperVoice, SynthesisConfig

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RIG = os.environ.get("REEL_RIG", os.path.dirname(ROOT))
MODEL = os.path.join(RIG, "models", "en_US-lessac-medium.onnx")
LEN_SCALE = float(os.environ.get("LEN_SCALE", "0.92"))  # <1 = a touch faster than default

cfg = json.load(open(os.path.join(ROOT, "script.json")))
voice = PiperVoice.load(MODEL)
sr = voice.config.sample_rate
syn = SynthesisConfig(length_scale=LEN_SCALE)

LEAD = 0.25  # silence before the first word
pcm = bytearray(b"\x00\x00" * int(LEAD * sr))
t = LEAD
segs = []
for line in cfg["lines"]:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        voice.synthesize_wav(line["say"], w, syn_config=syn)
    buf.seek(0)
    with wave.open(buf, "rb") as r:
        frames = r.readframes(r.getnframes())
    # trim Piper's own leading/trailing near-silence so our pauses are the real gaps
    samples = memoryview(frames).cast("h")
    thr = 300
    s = next((i for i, v in enumerate(samples) if abs(v) > thr), 0)
    e = len(samples) - next((i for i, v in enumerate(reversed(samples)) if abs(v) > thr), 0)
    s = max(0, s - int(0.02 * sr)); e = min(len(samples), e + int(0.05 * sr))
    body = frames[s * 2:e * 2]
    dur = (e - s) / sr
    chunks = [c.strip() for c in line["show"].split(" / ")]
    weights = [max(1, len(re.sub(r"[^A-Za-z0-9$#]", "", c))) for c in chunks]
    tot = sum(weights); ct = t; cks = []
    for c, wgt in zip(chunks, weights):
        d = dur * wgt / tot
        cks.append({"text": c, "start": round(ct, 3), "end": round(ct + d, 3)})
        ct += d
    segs.append({"id": line["id"], "scene": line["scene"], "start": round(t, 3),
                 "end": round(t + dur, 3), "chunks": cks})
    pcm += body
    pcm += b"\x00\x00" * int(line["pause"] * sr)
    t += dur + line["pause"]
    print(f'{line["id"]:>3} {dur:5.2f}s  {line["say"]}')

os.makedirs(os.path.join(ROOT, "public"), exist_ok=True)
with wave.open(os.path.join(ROOT, "public", "vo.wav"), "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(bytes(pcm))
json.dump({"total": round(t, 3), "segments": segs}, open(os.path.join(ROOT, "src", "timing.json"), "w"), indent=1)
print(f"total {t:.2f}s")
