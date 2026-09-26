"""Render a Reg Intel Daily podcast script to MP3 with the house voice.

Usage: python3 tts.py SCRIPT.txt OUTPUT.mp3
SCRIPT.txt: plain text, one paragraph per blank-line-separated block (spoken text only).
Needs: pip install kokoro-onnx soundfile --break-system-packages, ffmpeg, and
kokoro-v1.0.onnx + voices-v1.0.bin in the current directory (from
https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0).
Prints the duration in seconds.
"""
import re, sys, subprocess, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

VOICE, SPEED, SENTENCE_PAUSE, PARA_GAP = "am_eric", 1.05, 0.35, 0.6   # "Voice F", chosen 2026-09-26
# Exact phonemes for words the engine gets wrong. OSFI = OSS-FEE, equal stress on both syllables.
PHONEMES = {"OSFI's": "ˈɑːsfˈiːz", "OSFI": "ˈɑːsfˈiː"}
# Spelling substitutions. Reg has a HARD g (as in "girl").
SUBS = [(r"\bReg Intel", "Regg Intel"), (r"\bTLAC\b", "Tee-lack"), (r"\bDORA\b", "Dora"),
        (r"\bMRAs\b", "M R A's"), (r"\bMRA\b", "M R A"), (r"\bFDIC\b", "F D I C"), (r"\bOCC\b", "O C C"),
        (r"\bFCA\b", "F C A"), (r"\bRBC's\b", "R B C's"), (r"\bRBC\b", "R B C"), (r"\bB-12\b", "B twelve"),
        (r"\bGENIUS\b", "Genius"), (r"\bPRA\b", "P R A"), (r"\bEBA\b", "E B A"), (r"\bSEC\b", "S E C"),
        (r"\bOFAC\b", "Oh-fack"), (r"\bFINTRAC\b", "Fin-trak"), (r"\bFinCEN\b", "Fin-sen"), (r"\bD-SIBs?\b", "D-sibs")]

k = Kokoro("kokoro-v1.0.onnx", "voices-v1.0.bin")

def to_phonemes(text):
    for a, b in SUBS:
        text = re.sub(a, b, text)
    pattern = r"\b(" + "|".join(re.escape(w) for w in sorted(PHONEMES, key=len, reverse=True)) + r")\b"
    out = []
    for part in re.split(pattern, text):
        if part in PHONEMES:
            out.append(PHONEMES[part])
        elif part.strip():
            out.append(k.tokenizer.phonemize(part, "en-us"))
    return " ".join(out)

def main(src, dst):
    paras = [p.strip() for p in open(src, encoding="utf-8").read().split("\n\n") if p.strip()]
    chunks, sr = [], 24000
    for p in paras:
        s, sr = k.create(to_phonemes(p), voice=VOICE, speed=SPEED, is_phonemes=True, sentence_pause=SENTENCE_PAUSE)
        chunks += [s, np.zeros(int(sr * PARA_GAP), dtype=s.dtype)]
    audio = np.concatenate(chunks)
    sf.write("_tmp.wav", audio, sr)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "_tmp.wav", "-codec:a", "libmp3lame", "-b:a", "96k", dst], check=True)
    print(round(len(audio) / sr))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
