import sys


# ------------------------------------------------
# Scintilla capture loop
# ------------------------------------------------

def capture_loop():

    # Lazy import so Whisper does not load unless needed
    from azq.scintilla import capture, transcribe, extract

    print("\nCole Scintilla")
    print("Gather Sparks\n")

    print("1 → start recording")
    print("2 → stop recording")
    print("3 → discard recording")
    print("4 → exit\n")

    while True:

        cmd = input("Command: ").strip()

        if cmd == "1":

            audio = capture.record()

            if audio is None:
                continue

            transcript = transcribe.run(audio)

            extract.run(transcript)

            print("\nSpark captured.\n")

        elif cmd == "4":

            print("Exiting Scintilla.")
            break


# ------------------------------------------------
# CLI entry
# ------------------------------------------------


def ensure_finis_storage_ready():
    """Run the Stage 1 Finis migration trigger before active goal commands."""
    from azq.finis.storage import LegacyGoalsError, ensure_canonical_goals_migrated

    try:
        migration = ensure_canonical_goals_migrated()
    except LegacyGoalsError as exc:
        print(f"Finis migration failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    if migration["triggered"]:
        print("Finis migration: data/finis/goals.json -> data/finis/goals/")
        print(
            "Migrated "
            f"{migration['migrated']} goal(s); "
            f"{migration['skipped']} already had canonical files."
        )
        print()


def main():

    if len(sys.argv) < 2:

        print("Commands:")
        print("  capture")
        print("  sparks")
        print("  spark <id>")
        print("  spark rm <id>")
        print("  spark search <text>")
        print("  fine")
        print("  goals")
        print("  goal add")
        print("  goal close <id>")
        print("  goal archive <id>")
        print("  azq form build <goal_id>")
        print("  azq form list")
        print("  azq form show <deliverable_id>")
        print("  azq form map <goal_id>")

        return

    cmd = sys.argv[1]

    # ---------------------------------------------
    # Capture
    # ---------------------------------------------

    if cmd == "capture":

        capture_loop()

    # ---------------------------------------------
    # List sparks
    # ---------------------------------------------

    elif cmd == "sparks":

        from azq.scintilla.sparks import list_sparks
        list_sparks()

    # ---------------------------------------------
    # Spark operations
    # ---------------------------------------------

    elif cmd == "spark":

        if len(sys.argv) < 3:
            print("Usage: azq spark <id>")
            return

        sub = sys.argv[2]

        if sub == "rm":

            if len(sys.argv) < 4:
                print("Usage: azq spark rm <id>")
                return

            from azq.scintilla.spark_delete import delete_spark
            delete_spark(sys.argv[3])

        elif sub == "search":

            if len(sys.argv) < 4:
                print("Usage: azq spark search <text>")
                return

            from azq.scintilla.spark_search import search_sparks
            search_sparks(" ".join(sys.argv[3:]))

        else:

            from azq.scintilla.spark_view import view_spark
            view_spark(sub)

    # ---------------------------------------------
    # Finis engine
    # ---------------------------------------------

    elif cmd == "fine":
        ensure_finis_storage_ready()

        from azq.finis.fine import run_fine
        run_fine()

    # ---------------------------------------------
    # List goals
    # ---------------------------------------------

    elif cmd == "goals":
        ensure_finis_storage_ready()

        from azq.finis.goals import show_goals
        show_goals()

    # ---------------------------------------------
    # Goal operations
    # ---------------------------------------------

    elif cmd == "goal":

        if len(sys.argv) < 3:
            print("Usage: azq goal [add|close|archive]")
            return

        ensure_finis_storage_ready()

        sub = sys.argv[2]

        if sub == "add":

            from azq.finis.goal_manager import add_goal
            add_goal()

        elif sub == "close":

            if len(sys.argv) < 4:
                print("Usage: azq goal close <id>")
                return

            from azq.finis.goal_manager import close_goal
            close_goal(sys.argv[3])

        elif sub == "archive":

            if len(sys.argv) < 4:
                print("Usage: azq goal archive <id>")
                return

            from azq.finis.goal_manager import archive_goal
            archive_goal(sys.argv[3])

    # ---------------------------------------------
    # Formam engine
    # ---------------------------------------------

    elif cmd == "form":

        if len(sys.argv) < 3:
            print("Usage: azq form [build|list|show|map]")
            return

        sub = sys.argv[2]

        if sub == "build":

            if len(sys.argv) < 4:
                print("Usage: azq form build <goal_id>")
                return

            ensure_finis_storage_ready()

            from azq.formam.build import build_form
            build_form(sys.argv[3])

        elif sub == "list":

            from azq.formam.deliverables import list_deliverables
            list_deliverables()

        elif sub == "show":

            if len(sys.argv) < 4:
                print("Usage: azq form show <deliverable_id>")
                return

            from azq.formam.deliverables import show_deliverable
            show_deliverable(sys.argv[3])

        elif sub == "map":

            if len(sys.argv) < 4:
                print("Usage: azq form map <goal_id>")
                return

            ensure_finis_storage_ready()

            from azq.formam.maps import form_map
            form_map(sys.argv[3])

        else:
            print("Usage: azq form [build|list|show|map]")

    else:

        print("Unknown command:", cmd)
