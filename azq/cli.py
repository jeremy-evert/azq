import sys

from azq.agenda.router import dispatch as dispatch_agenda
from azq.finis.router import dispatch as dispatch_finis
from azq.formam.router import dispatch as dispatch_formam
from azq.scintilla.router import dispatch as dispatch_scintilla


def print_commands() -> None:
    """Print the live Stage 3 top-level command listing."""
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
    print("  form build <goal_id>")
    print("  form list")
    print("  form show <deliverable_id>")
    print("  form map <goal_id>")
    print("  agenda build <deliverable_id>")
    print("  agenda list")
    print("  agenda show <task_id>")
    print("  agenda dag <deliverable_id>")


def main():
    argv = sys.argv[1:]
    if not argv:
        print_commands()
        return

    for dispatch in (
        dispatch_scintilla,
        dispatch_finis,
        dispatch_formam,
        dispatch_agenda,
    ):
        if dispatch(argv):
            return

    print("Unknown command:", argv[0])
