import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
from pathlib import Path
from datetime import datetime
import sys

SAMPLE_RATE = 16000
OUT = Path("data/scintilla/audio")
OUT.mkdir(parents=True, exist_ok=True)


def record():

    frames = []

    def callback(indata, frame_count, time, status):
        frames.append(indata.copy())

    stream = sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        callback=callback
    )

    stream.start()

    while True:
        cmd = input().strip()
        if cmd == "2":
            break

    stream.stop()
    stream.close()

    audio = np.concatenate(frames, axis=0)

    # normalize volume
    max_val = np.max(np.abs(audio))
    if max_val > 0:
        audio = audio / max_val

    # trim silence
    threshold = 0.01
    mask = np.abs(audio) > threshold

    if np.any(mask):
        start = np.argmax(mask)
        end = len(audio) - np.argmax(mask[::-1])
        audio = audio[start:end]

    filename = datetime.now().strftime("%Y-%m-%d_%H%M%S") + ".wav"
    path = OUT / filename

    write(path, SAMPLE_RATE, audio)

    print(f"Saved audio: {path}")

    return path
