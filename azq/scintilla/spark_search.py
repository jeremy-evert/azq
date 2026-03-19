from azq.scintilla.storage import list_spark_files, load_spark_file


def search_sparks(text):

    text = text.lower()

    files = list_spark_files()

    matches = []

    for f in files:

        data = load_spark_file(f)

        for s in data:

            spark = s.get("spark", "").lower()

            if text in spark:
                matches.append((f.stem, spark))

    if not matches:
        print("No matches.")
        return

    print("\nMatches\n")

    for sid, spark in matches:
        print(sid)
        print(f"  - {spark}")
        print()
