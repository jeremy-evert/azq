"""Scintilla command routing for the top-level AZQ CLI."""


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


def dispatch(argv: list[str]) -> bool:
    """Handle Scintilla commands and return True when one was dispatched."""
    if not argv:
        return False

    cmd = argv[0]

    if cmd == "capture":
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
