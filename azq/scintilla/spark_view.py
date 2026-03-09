import json
from pathlib import Path


AUDIO_DIR = Path("data/scintilla/audio")
TRANSCRIPT_DIR = Path("data/scintilla/transcripts")
SPARK_DIR = Path("data/scintilla/sparks")


def view_spark(spark_id):

    audio = AUDIO_DIR / f"{spark_id}.wav"
    transcript = TRANSCRIPT_DIR / f"{spark_id}.txt"
    sparks = SPARK_DIR / f"{spark_id}.json"

    print(f"\nSpark ID: {spark_id}\n")

    if transcript.exists():
        print("Transcript")
        print("----------")
        print(transcript.read_text())
        print()

    else:
        print("Transcript not found.\n")

    if sparks.exists():

        print("Extracted Sparks")
        print("----------------")

        data = json.loads(sparks.read_text())

        for i, s in enumerate(data, 1):
            print(f"{i}. {s.get('spark')}")

        print()

    else:
        print("No sparks file found.\n")

    print("Artifacts")
    print("---------")

    print(f"audio: {audio}")
    print(f"transcript: {transcript}")
    print(f"sparks: {sparks}")
