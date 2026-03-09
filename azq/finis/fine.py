import json
from pathlib import Path
from .goals import load_goals, save_goals, next_goal_id

SPARK_DIR = Path("data/scintilla/sparks")


def load_sparks():
    sparks = []

    for file in sorted(SPARK_DIR.glob("*.json")):
        with open(file) as f:
            data = json.load(f)

        for s in data:
            sparks.append(
                {
                    "spark": s["spark"],
                    "source": file.name
                }
            )

    return sparks
