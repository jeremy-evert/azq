import difflib
import json
from datetime import date
from pathlib import Path

from . import storage

SPARK_DIR = Path("data/scintilla/sparks")
TITLE_DEDUPE_THRESHOLD = 0.39


# ------------------------------------------------
# Load sparks
# ------------------------------------------------

def load_sparks():
    """Read all spark files."""

    sparks = []

    for file in sorted(SPARK_DIR.glob("*.json")):

        with open(file) as f:
            data = json.load(f)

        for spark_index, s in enumerate(data, start=1):

            sparks.append(
                {
                    "spark": s["spark"],
                    "source": file.stem,
                    "spark_index": spark_index,
                }
            )

    return sparks


# ------------------------------------------------
# Similarity check
# ------------------------------------------------

def similar(a, b):
    """Return similarity ratio between two strings."""
    return difflib.SequenceMatcher(None, a, b).ratio()


# ------------------------------------------------
# Goal text cleanup
# ------------------------------------------------

def clean_goal_text(text):
    """
    Convert spoken phrases into better goal statements.
    """

    text = text.strip()

    prefixes = [
        "i would like to",
        "i want to",
        "my goal is to",
        "one of the goals that i have is",
        "one goal is to",
        "the goal is to",
    ]

    lower = text.lower()

    for p in prefixes:
        if lower.startswith(p):
            text = text[len(p) :].strip()

    # normalize whitespace
    text = " ".join(text.split())

    # capitalize nicely
    text = text[0].upper() + text[1:]

    return text


# ------------------------------------------------
# Extract used spark sources
# ------------------------------------------------

def get_used_sources(goals):

    used = set()

    for g in goals:
        for s in g.get("derived_from", []):
            used.add(s)

    return used


# ------------------------------------------------
# Propose goals
# ------------------------------------------------

def propose_goals(sparks):

    existing_goals = storage.load_all_goals(migrate_legacy=True)

    existing_text = [g["title"].lower() for g in existing_goals]

    used_sources = get_used_sources(existing_goals)

    candidates = []

    for s in sparks:

        source = s["source"]

        # skip sparks already used
        if source in used_sources:
            continue

        raw_text = s["spark"].strip()

        if len(raw_text) < 10:
            continue

        candidate_text = clean_goal_text(raw_text)
        text_lower = candidate_text.lower()

        duplicate = False

        for g in existing_text:
            # Fine works with short candidate titles, so a lower threshold keeps
            # obvious title-level duplicates from slipping through canonical
            # storage as new goal files.
            if similar(text_lower, g) >= TITLE_DEDUPE_THRESHOLD:
                duplicate = True
                break

        if duplicate:
            continue

        candidates.append(
            {
                "review_id": f"REVIEW_{source}_{s['spark_index']:03d}",
                "source": source,
                "raw_spark_text": raw_text,
                "candidate_goal_text": candidate_text,
            }
        )

    return candidates


# ------------------------------------------------
# Materialize review artifacts
# ------------------------------------------------

def write_candidate_reviews(candidates):
    """Persist one durable Finis review artifact per candidate goal."""

    written = []

    for candidate in candidates:
        review_record = {
            "review_id": candidate["review_id"],
            "spark_source": candidate["source"],
            "raw_spark_text": candidate["raw_spark_text"],
            "candidate_goal_text": candidate["candidate_goal_text"],
            "human_revision_text": "",
            "review_status": "pending",
            "accepted_goal_id": "",
        }
        storage.write_review(review_record)
        written.append(review_record)

    return written


# ------------------------------------------------
# Confirm goals interactively
# ------------------------------------------------

def confirm_goals(review_records):

    confirmed = []

    if not review_records:
        return confirmed

    print("\nCandidate Goals\n")

    for i, review_record in enumerate(review_records):

        print(f"{i+1}. {review_record['candidate_goal_text']}")

        ans = input("Accept goal? [y/n] ")

        if ans.lower().startswith("y"):
            confirmed.append(review_record)

        print()

    return confirmed


# ------------------------------------------------
# Promote accepted reviews
# ------------------------------------------------

def promote_accepted_reviews(accepted_reviews):
    """Promote accepted review state into canonical goals and update reviews."""

    for review_record in accepted_reviews:
        goal_id = storage.next_goal_id()
        goal_record = {
            "goal_id": goal_id,
            "title": review_record["candidate_goal_text"],
            "status": "active",
            "created": str(date.today()),
            "description": "",
            "derived_from": [review_record["spark_source"]],
        }
        storage.write_goal(goal_record)

        accepted_review_record = dict(review_record)
        accepted_review_record["review_status"] = "accepted"
        accepted_review_record["accepted_goal_id"] = goal_id
        storage.write_review(accepted_review_record)


# ------------------------------------------------
# Main Finis engine
# ------------------------------------------------

def run_fine():

    sparks = load_sparks()

    if not sparks:
        print("No sparks found.")
        return

    candidates = propose_goals(sparks)

    if not candidates:
        print("No candidate goals to review.")
        return

    review_records = write_candidate_reviews(candidates)
    print("\nReviews written to data/finis/reviews/")

    accepted_reviews = confirm_goals(review_records)

    if not accepted_reviews:
        print("No goals confirmed.")
        return

    promote_accepted_reviews(accepted_reviews)

    print("\nGoals written to data/finis/goals/")
