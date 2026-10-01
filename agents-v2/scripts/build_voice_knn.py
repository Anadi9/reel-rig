#!/usr/bin/env python3
"""Character voiceover, best-of-N per line: Piper (stochastic) → kNN-VC into the character's voice →
Whisper base.en check → keep the take whose transcript best matches the caption text.

Writes public/vo.wav (16 kHz, the character's voice), public/vo_piper.wav (the chosen Piper takes, same
timing) and src/timing.json. Takes are cached in .takes/ so a re-run only redoes changed lines.
Env: TAKES (default 5), LEN_SCALE (0.9), KNNVC_DIR, ASR_DIR. Run from agents-v2/.
"""
import difflib, hashlib, io, json, os, re, sys, wave
import numpy as np, soundfile as sf, torch, torchaudio
from piper import PiperVoice, SynthesisConfig

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RIG = os.environ.get("REEL_RIG", os.path.dirname(ROOT))
TAKES = int(os.environ.get("TAKES", "5"))
LEN_SCALE = float(os.environ.get("LEN_SCALE", "0.9"))
SR = 16000
CACHE = os.path.join(ROOT, ".takes"); os.makedirs(CACHE, exist_ok=True)

def _load(p, *a, **k):
    x, sr = sf.read(p, dtype="float32", always_2d=True)
    return torch.from_numpy(x.T.copy()), sr
torchaudio.load = _load
sys.path.insert(0, os.environ.get("KNNVC_DIR", "/home/user/vc/knn-vc"))
from hubconf import knn_vc  # noqa: E402
import glob, subprocess, tempfile, librosa, sherpa_onnx  # noqa: E402

torch.set_num_threads(os.cpu_count() or 4)
vc = knn_vc(pretrained=True, progress=False, prematched=True, device="cpu")
mpath = os.path.join(CACHE, "matching.pt")
if os.path.exists(mpath):
    matching = torch.load(mpath)
else:
    refs = [os.path.join(RIG, "voice-reference.wav")] + sorted(glob.glob(os.path.join(RIG, ".voice-work", "*", "cloned.wav")))
    tmp = tempfile.mkdtemp(); paths = []
    for i, r in enumerate(refs):
        q = os.path.join(tmp, f"{i}.wav"); subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", r, "-ac", "1", "-ar", "16000", q], check=True); paths.append(q)
    matching = vc.get_matching_set(paths, vad_trigger_level=0); torch.save(matching, mpath)

M = os.environ.get("ASR_DIR", "/home/user/vc/asr/sherpa-onnx-whisper-base.en")
asr = sherpa_onnx.OfflineRecognizer.from_whisper(encoder=f"{M}/base.en-encoder.int8.onnx", decoder=f"{M}/base.en-decoder.int8.onnx",
                                                 tokens=f"{M}/base.en-tokens.txt", language="en", task="transcribe")
voice = PiperVoice.load(os.path.join(RIG, "models", "en_US-lessac-medium.onnx"))
norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower().replace("#1", "number one").replace("no. 1", "number one").replace("number 1", "number one"))

def piper_take(text):
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        voice.synthesize_wav(text, w, syn_config=SynthesisConfig(length_scale=LEN_SCALE))
    buf.seek(0); r = wave.open(buf)
    x = np.frombuffer(r.readframes(r.getnframes()), np.int16).astype(np.float32) / 32768
    x = librosa.resample(x, orig_sr=r.getframerate(), target_sr=SR)
    nz = np.where(np.abs(x) > 0.01)[0]
    return x[max(0, nz[0] - 320): nz[-1] + 800] if len(nz) else x

def convert(x):
    q = vc.get_features(torch.from_numpy(x)[None], vad_trigger_level=0)
    return vc.match(q, matching, topk=4).cpu().numpy()

def hear(y):
    st = asr.create_stream(); st.accept_waveform(SR, np.concatenate([np.zeros(800, np.float32), y, np.zeros(1600, np.float32)])); asr.decode_stream(st)
    return st.result.text.strip()

cfg = json.load(open(os.path.join(ROOT, "script.json")))
out_c, out_p, segs = [np.zeros(int(0.25 * SR), np.float32)], [np.zeros(int(0.25 * SR), np.float32)], []
t = 0.25
for line in cfg["lines"]:
    want = norm(line["show"].replace(" / ", " "))
    key = hashlib.md5(f'{line["say"]}|{LEN_SCALE}'.encode()).hexdigest()[:10]
    best = None
    for k in range(TAKES):
        f = os.path.join(CACHE, f'{line["id"]}_{key}_{k}.npz')
        if os.path.exists(f):
            z = np.load(f); p, c, heard = z["p"], z["c"], str(z["heard"])
        else:
            p = piper_take(line["say"]); c = convert(p); heard = hear(c)
            np.savez(f, p=p, c=c, heard=heard)
        score = difflib.SequenceMatcher(None, norm(heard), want).ratio()
        if best is None or score > best[0]:
            best = (score, p, c, heard, k)
        if score >= 0.97:
            break
    score, p, c, heard, k = best
    n = min(len(p), len(c)); p, c = p[:n], c[:n]
    dur = n / SR
    chunks = [x.strip() for x in line["show"].split(" / ")]
    wts = [max(1, len(re.sub(r"[^A-Za-z0-9$#]", "", x))) for x in chunks]
    ct, cks = t, []
    for x, wgt in zip(chunks, wts):
        d = dur * wgt / sum(wts); cks.append({"text": x, "start": round(ct, 3), "end": round(ct + d, 3)}); ct += d
    segs.append({"id": line["id"], "scene": line["scene"], "start": round(t, 3), "end": round(t + dur, 3), "chunks": cks, "heard": heard, "match": round(score, 3)})
    gap = np.zeros(int(line["pause"] * SR), np.float32)
    out_c += [c, gap]; out_p += [p, gap]
    t += dur + line["pause"]
    print(f'{line["id"]:>3} take {k} match {score:.2f}  {heard}')

sf.write(os.path.join(ROOT, "public", "vo.wav"), np.concatenate(out_c), SR)
sf.write(os.path.join(ROOT, "public", "vo_piper.wav"), np.concatenate(out_p), SR)
json.dump({"total": round(t, 3), "segments": segs}, open(os.path.join(ROOT, "src", "timing.json"), "w"), indent=1)
print(f"total {t:.2f}s")
