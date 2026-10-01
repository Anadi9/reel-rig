#!/usr/bin/env python3
"""Convert the Piper voiceover into the character's voice with kNN-VC (cloud fallback for OpenVoice).

kNN-VC swaps every WavLM frame of the source for its nearest frames in a reference set, then vocodes.
Reference set = the real voice-reference.wav + every shipped OpenVoice clone in .voice-work/*/cloned.wav
(~8 min of the character's voice; more reference = cleaner output).

Needs: torch, torchaudio, the knn-vc repo (git clone https://github.com/bshall/knn-vc) at $KNNVC_DIR
(default /home/user/vc/knn-vc) and its two release checkpoints in ~/.cache/torch/hub/checkpoints.
Usage: python3 scripts/clone_knnvc.py public/vo_piper.wav public/vo.wav
"""
import glob, os, subprocess, sys, tempfile
import soundfile as sf
import torch, torchaudio

# torchaudio >= 2.9 routes load/save through torchcodec; plain soundfile is enough for 16k mono wavs
def _load(p, *a, **k):
    x, sr = sf.read(p, dtype="float32", always_2d=True)
    return torch.from_numpy(x.T.copy()), sr
torchaudio.load = _load

src, out = sys.argv[1], sys.argv[2]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RIG = os.environ.get("REEL_RIG", os.path.dirname(ROOT))
sys.path.insert(0, os.environ.get("KNNVC_DIR", "/home/user/vc/knn-vc"))
from hubconf import knn_vc  # noqa: E402

refs = [os.path.join(RIG, "voice-reference.wav")] + sorted(glob.glob(os.path.join(RIG, ".voice-work", "*", "cloned.wav")))
tmp = tempfile.mkdtemp()

def to16k(p):
    q = os.path.join(tmp, f"{abs(hash(p))}.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", p, "-ac", "1", "-ar", "16000", q], check=True)
    return q

torch.set_num_threads(os.cpu_count() or 4)
vc = knn_vc(pretrained=True, progress=False, prematched=True, device="cpu")
matching = vc.get_matching_set([to16k(r) for r in refs], vad_trigger_level=0)
query = vc.get_features(to16k(src))
wav = vc.match(query, matching, topk=int(os.environ.get("TOPK", "4")))
sf.write(out, wav.cpu().numpy(), 16000)
print(f"{out}: {wav.shape[0] / 16000:.2f}s from {len(refs)} reference clips")
