from pathlib import Path
import json
from azq.scintilla.storage import ensure_scintilla_dirs, spark_file_path

ensure_scintilla_dirs()


def run(transcript_file):

    text = Path(transcript_file).read_text()

    parts = text.split(".")

    sparks = []

    for p in parts:
        p = p.strip()

        if len(p) > 10:
            sparks.append(
                {
                    "spark": p.lower(),
                    "confidence": 0.5
                }
            )

    name = Path(transcript_file).stem
    outfile = spark_file_path(name)

    with open(outfile, "w", encoding="utf-8") as f:
        json.dump(sparks, f, indent=2)

    print(f"Sparks: {outfile}")

    return outfile
