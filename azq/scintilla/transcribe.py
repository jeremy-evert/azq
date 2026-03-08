from pathlib import Path
import whisper

OUT = Path("data/scintilla/transcripts")
OUT.mkdir(parents=True, exist_ok=True)

print("Loading Whisper model...")
MODEL = whisper.load_model("base")
print("Whisper ready")


def run(audio_file):

    result = MODEL.transcribe(str(audio_file))

    transcript = result["text"]

    name = Path(audio_file).stem
    outfile = OUT / f"{name}.txt"

    with open(outfile, "w") as f:
        f.write(transcript)

    print(f"Transcript: {outfile}")

    return outfile
