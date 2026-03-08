from pathlib import Path
import whisper

OUT = Path("data/scintilla/transcripts")
OUT.mkdir(parents=True, exist_ok=True)


def run(audio_file):

    model = whisper.load_model("base")

    result = model.transcribe(str(audio_file))

    transcript = result["text"]

    name = Path(audio_file).stem
    outfile = OUT / f"{name}.txt"

    with open(outfile, "w") as f:
        f.write(transcript)

    print(f"Transcript: {outfile}")

    return outfile
