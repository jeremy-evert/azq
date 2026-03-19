from azq.scintilla.storage import spark_artifact_paths


def delete_spark(spark_id):

    artifacts = spark_artifact_paths(spark_id)
    files = [artifacts["audio"], artifacts["transcript"], artifacts["sparks"]]

    removed = False

    for f in files:

        if f.exists():
            f.unlink()
            removed = True

    if removed:
        print(f"Removed spark {spark_id}")
    else:
        print("Nothing removed.")
