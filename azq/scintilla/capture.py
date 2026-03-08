from datetime import datetime
from pathlib import Path
import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np

AUDIO_DIR = Path("data/scintilla/audio")
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

SAMPLE_RATE = 44100


def record():

    print("\nRecording started (press 2 to stop)...")

    recording = []

    def callback(indata, frames, time, status):
        recording.append(indata.copy())

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

        if cmd == "3":
            print("Recording discarded.")
            stream.stop()
            return None

    stream.stop()

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    filename = AUDIO_DIR / f"{timestamp}.wav"

    audio = np.concatenate(recording, axis=0)
    write(filename, SAMPLE_RATE, audio)

    print(f"Saved audio: {filename}")

    return filename
