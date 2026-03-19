from pathlib import Path
import whisper
import torch
from azq.scintilla.storage import ensure_scintilla_dirs, transcript_file_path

ensure_scintilla_dirs()

print("Loading Whisper model...")

# ------------------------------------------------
# Decide device safely
# ------------------------------------------------

if torch.cuda.is_available():
    DEVICE = "cuda"
    print("CUDA detected")
else:
    DEVICE = "cpu"
    print("Running on CPU")

# ------------------------------------------------
# Load models once
# ------------------------------------------------

MODEL = whisper.load_model("small", device=DEVICE)

CPU_MODEL = None
if DEVICE == "cuda":
    CPU_MODEL = whisper.load_model("small", device="cpu")

print("Whisper ready")


def _safe_transcribe(model, audio_file):
    """
    Runs whisper transcription with safe settings.
    """

    result = model.transcribe(
        str(audio_file),
        language="en",
        temperature=0,
        fp16=False
    )

    text = result.get("text", "").strip()

    return text


def run(audio_file):

    audio_file = Path(audio_file)

    print(f"Transcribing: {audio_file.name}")

    # ---------------------------------------------
    # First attempt
    # ---------------------------------------------

    try:

        transcript = _safe_transcribe(MODEL, audio_file)

        # detect pathological outputs
        if not transcript or transcript.count("!") > 10:
            raise RuntimeError("Whisper produced invalid output")

    except Exception as e:

        print("Primary transcription failed:", e)

        if CPU_MODEL is None:
            raise

        print("Retrying on CPU model...")

        transcript = _safe_transcribe(CPU_MODEL, audio_file)

    # ---------------------------------------------
    # Save transcript
    # ---------------------------------------------

    name = audio_file.stem
    outfile = transcript_file_path(name)

    with open(outfile, "w", encoding="utf-8") as f:
        f.write(transcript)

    print(f"Transcript saved → {outfile}")

    return outfile
