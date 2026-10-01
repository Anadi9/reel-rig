#!/usr/bin/env python3
"""Transcribe each script line's slice of a voiceover with Whisper base.en (sherpa-onnx, offline) and print it
next to the script, so mispronunciations show up before rendering.
Usage: python3 scripts/check_transcript.py public/vo.wav   (model dir: $ASR_DIR, default /home/user/vc/asr/sherpa-onnx-whisper-base.en)
"""
import json, os, sys
import librosa, sherpa_onnx

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = os.environ.get("ASR_DIR", "/home/user/vc/asr/sherpa-onnx-whisper-base.en")
rec = sherpa_onnx.OfflineRecognizer.from_whisper(encoder=f"{M}/base.en-encoder.int8.onnx", decoder=f"{M}/base.en-decoder.int8.onnx",
                                                 tokens=f"{M}/base.en-tokens.txt", language="en", task="transcribe")
y, sr = librosa.load(sys.argv[1], sr=16000)
T = json.load(open(os.path.join(ROOT, "src", "timing.json")))
cfg = {l["id"]: l for l in json.load(open(os.path.join(ROOT, "script.json")))["lines"]}
for s in T["segments"]:
    st = rec.create_stream()
    st.accept_waveform(sr, y[int((s["start"] - 0.05) * sr): int((s["end"] + 0.1) * sr)])
    rec.decode_stream(st)
    print(f'{s["id"]:>3}  SAY {cfg[s["id"]]["say"]}\n     HEARD {st.result.text.strip()}')
