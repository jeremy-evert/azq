import sys
from azq.scintilla import capture, transcribe, extract


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
        print("Commands: capture")
        return

    cmd = sys.argv[1]

    if cmd == "capture":
        capture_loop()
