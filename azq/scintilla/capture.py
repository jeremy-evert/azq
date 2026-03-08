from datetime import datetime
from pathlib import Path
import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
import sys
import sys
import tty
import termios

AUDIO_DIR = Path("data/scintilla/audio")
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

SAMPLE_RATE = 44100



def wait_for_space(prompt=""):
    print(prompt, flush=True)

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    try:
        tty.setraw(fd)

        while True:
            ch = sys.stdin.read(1)

            if ch == " ":
                return

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def record():

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    filename = AUDIO_DIR / f"{timestamp}.wav"

    wait_for_space("\nPress SPACE to start recording")

    print("Recording... press SPACE to stop")

    recording = []

    def callback(indata, frames, time, status):
        recording.append(indata.copy())

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, callback=callback):

        wait_for_space("")

    audio = np.concatenate(recording, axis=0)

    write(filename, SAMPLE_RATE, audio)

    print(f"Saved audio: {filename}")

    return filename
