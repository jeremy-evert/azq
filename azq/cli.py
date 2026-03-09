import sys

from azq.scintilla import capture, transcribe, extract
from azq.scintilla.sparks import list_sparks
from azq.scintilla.spark_view import view_spark
from azq.scintilla.spark_delete import delete_spark
from azq.scintilla.spark_search import search_sparks

from azq.finis.fine import run_fine
from azq.finis.goals import show_goals


def capture_loop():

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
        return

    cmd = sys.argv[1]

    if cmd == "capture":
        capture_loop()

    elif cmd == "sparks":
        list_sparks()

    elif cmd == "spark":

        if len(sys.argv) < 3:
            print("Usage: azq spark <id>")
            return

        sub = sys.argv[2]

        if sub == "rm":

            if len(sys.argv) < 4:
                print("Usage: azq spark rm <id>")
                return

            delete_spark(sys.argv[3])

        elif sub == "search":

            if len(sys.argv) < 4:
                print("Usage: azq spark search <text>")
                return

            search_sparks(" ".join(sys.argv[3:]))

        else:
            view_spark(sub)

    elif cmd == "fine":
        run_fine()

    elif cmd == "goals":
        show_goals()
