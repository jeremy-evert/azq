import sys

from azq.scintilla import capture
from azq.scintilla import transcribe
from azq.scintilla import extract


def capture_loop():

    print("\nCole Scintilla")
    print("Gather Sparks\n")
    print("SPACE = record")
    print("CTRL+C = exit\n")

    while True:

        audio = capture.record()

        input("Press ENTER to transcribe...")

        transcript = transcribe.run(audio)

        extract.run(transcript)

        print("\nSpark captured.\n")


def main():

    if len(sys.argv) < 2:
        print("Commands: capture")
        return

    cmd = sys.argv[1]

    if cmd == "capture":
        capture_loop()

    else:
        print("Unknown command")
