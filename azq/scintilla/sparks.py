import json
from pathlib import Path

SPARK_DIR = Path("data/scintilla/sparks")


def list_sparks():

    if not SPARK_DIR.exists():
        print("No sparks directory found.")
        return

    files = sorted(SPARK_DIR.glob("*.json"))

    if not files:
        print("No sparks found.")
        return

    print("\nScintillae\n")

    for f in files:

        spark_id = f.stem

        print(spark_id)

        try:
            data = json.loads(f.read_text())

            for s in data:
                text = s.get("spark", "")
                print(f"  - {text}")

        except Exception as e:
            print(f"  (error reading sparks: {e})")

        print()
