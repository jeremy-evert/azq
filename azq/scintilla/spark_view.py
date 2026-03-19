from azq.scintilla.storage import load_spark_artifact, spark_artifact_paths


def view_spark(spark_id):

    artifacts = spark_artifact_paths(spark_id)
    audio = artifacts["audio"]
    transcript = artifacts["transcript"]
    sparks = artifacts["sparks"]

    print(f"\nSpark ID: {spark_id}\n")

    if transcript.exists():
        print("Transcript")
        print("----------")
        print(transcript.read_text())
        print()

    else:
        print("Transcript not found.\n")

    if sparks.exists():

        print("Extracted Sparks")
        print("----------------")

        data = load_spark_artifact(spark_id) or []

        for i, s in enumerate(data, 1):
            print(f"{i}. {s.get('spark')}")

        print()

    else:
        print("No sparks file found.\n")

    print("Artifacts")
    print("---------")

    print(f"audio: {audio}")
    print(f"transcript: {transcript}")
    print(f"sparks: {sparks}")
