import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
from pathlib import Path
from datetime import datetime
import sys

SAMPLE_RATE = 16000
DEVICE = 9  # PipeWire default input

OUT = Path("data/scintilla/audio")
OUT.mkdir(parents=True, exist_ok=True)


def record():

    frames = []

    print("\n🟢 Mic armed (waiting for speech)\n")

    def callback(indata, frames_count, time, status):

        audio = indata.copy()
        frames.append(audio)

        level = float(np.max(np.abs(audio)))

        if level > 0.03:
            color = "\033[94m"
            symbol = "🔵 speech"
        else:
            color = "\033[92m"
            symbol = "🟢 quiet"

        sys.stdout.write(
            f"\r{color}{symbol} level={level:.4f}\033[0m"
        )
        sys.stdout.flush()

    # IMPORTANT: assign stream
    stream = sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        device=DEVICE,
        dtype="float32",
        blocksize=0,
        callback=callback
    )

    stream.start()

    while True:
        cmd = input()
        if cmd.strip() == "2":
            break

    stream.stop()
    stream.close()

    print("\n🔴 Mic stopped\n")

    if not frames:
        print("No audio captured.")
        return None

    audio = np.concatenate(frames, axis=0)

    # protect against clipping
    audio = np.clip(audio, -1.0, 1.0)

    print("Recorded samples:", len(audio))
    print("Peak amplitude:", np.max(np.abs(audio)))

    max_val = np.max(np.abs(audio))

    # normalize if strong enough
    if max_val > 0.01:
        audio = audio / max_val

    # trim silence
    threshold = 0.002
    mask = np.abs(audio) > threshold

    if np.any(mask):
        start = np.argmax(mask)
        end = len(audio) - np.argmax(mask[::-1])
        audio = audio[start:end]

    filename = datetime.now().strftime("%Y-%m-%d_%H%M%S") + ".wav"
    path = OUT / filename

    audio_int16 = (audio * 32767).astype(np.int16)
    write(path, SAMPLE_RATE, audio_int16)

    print(f"Saved audio: {path}")

    return path
