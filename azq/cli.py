import sys

from azq.scintilla import capture
from azq.scintilla import transcribe
from azq.scintilla import extract


def main():

    if len(sys.argv) < 2:
        print("Commands: capture | transcribe | extract")
        return

    cmd = sys.argv[1]

    if cmd == "capture":

        audio = capture.run()
        transcript = transcribe.run(audio)
        extract.run(transcript)

    elif cmd == "transcribe":

        audio = sys.argv[2]
        transcribe.run(audio)

    elif cmd == "extract":

        transcript = sys.argv[2]
        extract.run(transcript)

    else:
        print("Unknown command")
