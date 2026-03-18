"""Finis command routing for the top-level AZQ CLI."""

import sys


def ensure_finis_storage_ready() -> None:
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


def dispatch(argv: list[str]) -> bool:
    """Handle Finis commands and return True when one was dispatched."""
    if not argv:
        return False

    cmd = argv[0]

    if cmd == "fine":
        ensure_finis_storage_ready()

        from azq.finis.fine import run_fine

        run_fine()
        return True

    if cmd == "goals":
        ensure_finis_storage_ready()

        from azq.finis.goals import show_goals

        show_goals()
        return True

    if cmd != "goal":
        return False

    if len(argv) < 2:
        print("Usage: azq goal [add|close|archive]")
        return True

    ensure_finis_storage_ready()
    sub = argv[1]

    if sub == "add":
        from azq.finis.goal_manager import add_goal

        add_goal()
        return True

    if sub == "close":
        if len(argv) < 3:
            print("Usage: azq goal close <id>")
            return True

        from azq.finis.goal_manager import close_goal

        close_goal(argv[2])
        return True

    if sub == "archive":
        if len(argv) < 3:
            print("Usage: azq goal archive <id>")
            return True

        from azq.finis.goal_manager import archive_goal

        archive_goal(argv[2])
        return True

    return True
