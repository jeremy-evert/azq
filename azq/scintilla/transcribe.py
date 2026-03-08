from pathlib import Path
import whisper

OUT = Path("data/scintilla/transcripts")
OUT.mkdir(parents=True, exist_ok=True)

print("Loading Whisper model (GPU if available)...")
MODEL = whisper.load_model("base")
print("Whisper ready")


def run(audio_file):

    try:
        result = MODEL.transcribe(str(audio_file))
    except Exception as e:

        print("GPU transcription failed, retrying on CPU...")

        

        cpu_model = whisper.load_model("base", device="cpu")
        result = cpu_model.transcribe(str(audio_file), fp16=False)

    transcript = result["text"]

    name = Path(audio_file).stem
    outfile = OUT / f"{name}.txt"

    with open(outfile, "w") as f:
        f.write(transcript)

    print(f"Transcript: {outfile}")

    return outfile
