import sys

from azq.finis.router import dispatch as dispatch_finis
from azq.formam.router import dispatch as dispatch_formam
from azq.scintilla.router import dispatch as dispatch_scintilla


def print_commands() -> None:
    """Print the shared top-level Stage 2 command listing."""
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


def main():
    argv = sys.argv[1:]
    if not argv:
        print_commands()
        return

    for dispatch in (dispatch_scintilla, dispatch_finis, dispatch_formam):
        if dispatch(argv):
            return

    print("Unknown command:", argv[0])
