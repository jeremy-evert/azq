from pathlib import Path


AUDIO_DIR = Path("data/scintilla/audio")
TRANSCRIPT_DIR = Path("data/scintilla/transcripts")
SPARK_DIR = Path("data/scintilla/sparks")


def delete_spark(spark_id):

    files = [
        AUDIO_DIR / f"{spark_id}.wav",
        TRANSCRIPT_DIR / f"{spark_id}.txt",
        SPARK_DIR / f"{spark_id}.json",
    ]

    removed = False

    for f in files:

        if f.exists():
            f.unlink()
            removed = True

    if removed:
        print(f"Removed spark {spark_id}")
    else:
        print("Nothing removed.")
