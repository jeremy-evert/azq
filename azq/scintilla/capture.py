import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
from scipy.signal import resample_poly
from pathlib import Path
from datetime import datetime
import sys

TARGET_RATE = 16000

OUT = Path("data/scintilla/audio")
OUT.mkdir(parents=True, exist_ok=True)


def find_input_device():
    devices = sd.query_devices()

    for i, dev in enumerate(devices):
        if dev["max_input_channels"] > 0:
            return i, dev

    raise RuntimeError("No microphone input devices found")


def record():

    device_id, device_info = find_input_device()

    device_rate = int(device_info["default_samplerate"])
    channels = min(device_info["max_input_channels"], 2)

    print("\n🎤 Using input device:")
    print(f"   {device_id}: {device_info['name']}")
    print(f"   channels available: {device_info['max_input_channels']}")
    print(f"   device sample rate: {device_rate}\n")

    frames = []

    print("🟢 Mic armed (waiting for speech)\n")

    def callback(indata, frames_count, time, status):

        if status:
            print(status, file=sys.stderr)

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

    stream = sd.InputStream(
        samplerate=device_rate,
        device=device_id,
        channels=channels,
        dtype="float32",
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

    # convert stereo → mono
    if audio.ndim > 1:
        audio = np.mean(audio, axis=1)

    audio = np.clip(audio, -1.0, 1.0)

    print("Recorded samples:", len(audio))
    print("Peak amplitude:", np.max(np.abs(audio)))

    # normalize
    max_val = np.max(np.abs(audio))
    if max_val > 0.01:
        audio = audio / max_val

    # trim silence
    threshold = 0.002
    mask = np.abs(audio) > threshold

    if np.any(mask):
        start = np.argmax(mask)
        end = len(audio) - np.argmax(mask[::-1])
        audio = audio[start:end]

    # resample → whisper rate
    if device_rate != TARGET_RATE:
        print(f"Resampling {device_rate} → {TARGET_RATE}")
        audio = resample_poly(audio, TARGET_RATE, device_rate)

    filename = datetime.now().strftime("%Y-%m-%d_%H%M%S") + ".wav"
    path = OUT / filename

    audio_int16 = (audio * 32767).astype(np.int16)
    write(path, TARGET_RATE, audio_int16)

    print(f"Saved audio: {path}")

    return path
