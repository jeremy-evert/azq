from pathlib import Path
import json

OUT = Path("data/scintilla/sparks")
OUT.mkdir(parents=True, exist_ok=True)


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
    outfile = OUT / f"{name}.json"

    with open(outfile, "w") as f:
        json.dump(sparks, f, indent=2)

    print(f"Sparks: {outfile}")

    return outfile
