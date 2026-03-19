from azq.scintilla.storage import SPARKS_DIR, list_spark_files, load_spark_file


def list_sparks():

    if not SPARKS_DIR.exists():
        print("No sparks directory found.")
        return

    files = list_spark_files()

    if not files:
        print("No sparks found.")
        return

    print("\nScintillae\n")

    for f in files:

        spark_id = f.stem

        print(spark_id)

        try:
            data = load_spark_file(f)

            for s in data:
                text = s.get("spark", "")
                print(f"  - {text}")

        except Exception as e:
            print(f"  (error reading sparks: {e})")

        print()
