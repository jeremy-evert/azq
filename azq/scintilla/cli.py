"""Scintilla command routing for the top-level AZQ CLI."""

from azq.scintilla.storage import (
    allocate_spark_id,
    ensure_scintilla_dirs,
    transcript_file_path,
)


def capture_loop() -> None:
    """Run the interactive Scintilla capture loop."""
    from azq.scintilla import capture, extract, transcribe

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


def capture_text(text: str) -> str:
    """Create a transcript-first spark bundle from direct text input."""
    from azq.scintilla.extract import run as extract_run

    ensure_scintilla_dirs()
    spark_id = allocate_spark_id()
    transcript = transcript_file_path(spark_id)
    transcript.write_text(text.strip(), encoding="utf-8")
    extract_run(transcript)

    print(f"Transcript saved → {transcript}")
    print("\nSpark captured.\n")

    return spark_id


def dispatch(argv: list[str]) -> bool:
    """Handle Scintilla commands and return True when one was dispatched."""
    if not argv:
        return False

    cmd = argv[0]

    if cmd == "capture":
        if len(argv) > 1 and argv[1] == "text":
            if len(argv) < 3 or not " ".join(argv[2:]).strip():
                print('Usage: azq capture text "..."')
                return True

            capture_text(" ".join(argv[2:]))
            return True

        capture_loop()
        return True

    if cmd == "sparks":
        from azq.scintilla.sparks import list_sparks

        list_sparks()
        return True

    if cmd != "spark":
        return False

    if len(argv) < 2:
        print("Usage: azq spark <id>")
        return True

    sub = argv[1]

    if sub == "rm":
        if len(argv) < 3:
            print("Usage: azq spark rm <id>")
            return True

        from azq.scintilla.spark_delete import delete_spark

        delete_spark(argv[2])
        return True

    if sub == "search":
        if len(argv) < 3:
            print("Usage: azq spark search <text>")
            return True

        from azq.scintilla.spark_search import search_sparks

        search_sparks(" ".join(argv[2:]))
        return True

    from azq.scintilla.spark_view import view_spark

    view_spark(sub)
    return True
