#!/usr/bin/env python3
"""Generate the hotspot narration audio with Kokoro (open model, Apache-2.0, runs offline).

Reads  content/narration/<slug>.txt   writes  app/static/audio/<slug>.mp3  (mono 24 kHz, 56 kbps).

Setup (in a separate venv, these are build tools and are NOT in requirements.txt):
    python3 -m venv /tmp/kokoroenv && /tmp/kokoroenv/bin/pip install kokoro-onnx soundfile
    brew install ffmpeg
Run:
    /tmp/kokoroenv/bin/python content/make_narration.py            # default voice bf_emma
    /tmp/kokoroenv/bin/python content/make_narration.py --voice bm_george --speed 0.95
Model files (about 350 MB) are downloaded once to ~/.cache/kokoro-onnx.
British voices: bf_emma, bf_isabella, bf_alice, bf_lily, bm_george, bm_lewis, bm_daniel, bm_fable.
"""
import argparse
import os
import subprocess
import sys
import tempfile
import urllib.request

import soundfile as sf
from kokoro_onnx import Kokoro

REL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"
CACHE = os.path.expanduser("~/.cache/kokoro-onnx")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def fetch(name):
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, name)
    if not os.path.exists(path):
        print("downloading", name, "...")
        urllib.request.urlretrieve(REL + name, path)
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice", default="bf_emma")
    ap.add_argument("--speed", type=float, default=0.95)
    ap.add_argument("--lang", default="en-gb")
    ap.add_argument("--only", help="generate a single slug, e.g. main-entrance")
    a = ap.parse_args()

    kokoro = Kokoro(fetch("kokoro-v1.0.onnx"), fetch("voices-v1.0.bin"))
    src = os.path.join(ROOT, "content", "narration")
    out = os.path.join(ROOT, "app", "static", "audio")
    os.makedirs(out, exist_ok=True)
    slugs = sorted(f[:-4] for f in os.listdir(src) if f.endswith(".txt"))
    if a.only:
        slugs = [a.only]
    for slug in slugs:
        text = open(os.path.join(src, slug + ".txt"), encoding="utf-8").read().strip()
        samples, sr = kokoro.create(text, voice=a.voice, speed=a.speed, lang=a.lang)
        with tempfile.TemporaryDirectory() as tmp:
            wav = os.path.join(tmp, slug + ".wav")
            sf.write(wav, samples, sr)
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", wav, "-ac", "1", "-ar", "24000", "-b:a", "56k",
                            os.path.join(out, slug + ".mp3")], check=True)
        print(f"{slug}: {len(samples) / sr:4.1f} s")
    print("voice:", a.voice, "speed:", a.speed)


if __name__ == "__main__":
    sys.exit(main())
