import json
from pathlib import Path


SPARK_DIR = Path("data/scintilla/sparks")


def search_sparks(text):

    text = text.lower()

    files = sorted(SPARK_DIR.glob("*.json"))

    matches = []

    for f in files:

        data = json.loads(f.read_text())

        for s in data:

            spark = s.get("spark", "").lower()

            if text in spark:
                matches.append((f.stem, spark))

    if not matches:
        print("No matches.")
        return

    print("\nMatches\n")

    for sid, spark in matches:
        print(sid)
        print(f"  - {spark}")
        print()
