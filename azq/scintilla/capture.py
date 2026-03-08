from datetime import datetime
from pathlib import Path
import sounddevice as sd
from scipy.io.wavfile import write

DATA = Path("data/scintilla/audio")
DATA.mkdir(parents=True, exist_ok=True)

SAMPLE_RATE = 44100
SECONDS = 5


def run():

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    filename = DATA / f"{timestamp}.wav"

    print("Speak your thought...")

    audio = sd.rec(int(SECONDS * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1)
    sd.wait()

    write(filename, SAMPLE_RATE, audio)

    print(f"Saved: {filename}")

    return filename
