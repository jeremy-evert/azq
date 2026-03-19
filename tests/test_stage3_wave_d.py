import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from azq import cli


@contextlib.contextmanager
def working_directory(path: Path):
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


class Stage3WaveDRegressionTests(unittest.TestCase):
    def write_spark_bundle(
        self,
        spark_id: str,
        *,
        transcript: str,
        sparks: list[dict[str, str]],
        audio_bytes: bytes = b"wav",
    ) -> None:
        base = Path("data/scintilla")
        base.joinpath("audio").mkdir(parents=True, exist_ok=True)
        base.joinpath("transcripts").mkdir(parents=True, exist_ok=True)
        base.joinpath("sparks").mkdir(parents=True, exist_ok=True)

        base.joinpath("audio", f"{spark_id}.wav").write_bytes(audio_bytes)
        base.joinpath("transcripts", f"{spark_id}.txt").write_text(
            transcript,
            encoding="utf-8",
        )
        base.joinpath("sparks", f"{spark_id}.json").write_text(
            json.dumps(sparks, indent=2),
            encoding="utf-8",
        )

    def run_cli(self, argv: list[str]) -> str:
        output = io.StringIO()
        with mock.patch("sys.argv", ["azq", *argv]), contextlib.redirect_stdout(output):
            cli.main()
        return output.getvalue()

    def test_sparks_lists_canonical_spark_files_in_stable_filename_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            with working_directory(repo_root):
                self.write_spark_bundle(
                    "2026-03-19_1015",
                    transcript="Later transcript",
                    sparks=[{"spark": "Second visible spark"}],
                )
                self.write_spark_bundle(
                    "2026-03-19_0900",
                    transcript="Earlier transcript",
                    sparks=[{"spark": "First visible spark"}],
                )

                output = self.run_cli(["sparks"])

                self.assertLess(
                    output.index("2026-03-19_0900"),
                    output.index("2026-03-19_1015"),
                )
                self.assertIn("  - First visible spark", output)
                self.assertIn("  - Second visible spark", output)

    def test_spark_exact_id_reads_live_transcript_and_spark_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            with working_directory(repo_root):
                self.write_spark_bundle(
                    "2026-03-19_0900",
                    transcript="Transcript line one.\nTranscript line two.",
                    sparks=[
                        {"spark": "Preserve the exact-id seam"},
                        {"spark": "Show extracted sparks from live storage"},
                    ],
                )

                output = self.run_cli(["spark", "2026-03-19_0900"])

                self.assertIn("Spark ID: 2026-03-19_0900", output)
                self.assertIn("Transcript line one.\nTranscript line two.", output)
                self.assertIn("1. Preserve the exact-id seam", output)
                self.assertIn("2. Show extracted sparks from live storage", output)
                self.assertIn(
                    "audio: data/scintilla/audio/2026-03-19_0900.wav",
                    output,
                )
                self.assertIn(
                    "transcript: data/scintilla/transcripts/2026-03-19_0900.txt",
                    output,
                )
                self.assertIn(
                    "sparks: data/scintilla/sparks/2026-03-19_0900.json",
                    output,
                )

    def test_spark_search_reads_live_spark_text_from_canonical_storage(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            with working_directory(repo_root):
                self.write_spark_bundle(
                    "2026-03-19_0900",
                    transcript="Search transcript",
                    sparks=[{"spark": "Protect shared read-surface behavior"}],
                )
                self.write_spark_bundle(
                    "2026-03-19_1015",
                    transcript="Other transcript",
                    sparks=[{"spark": "Unrelated note"}],
                )

                output = self.run_cli(["spark", "search", "read-surface"])

                self.assertIn("Matches", output)
                self.assertIn("2026-03-19_0900", output)
                self.assertIn("  - protect shared read-surface behavior", output)
                self.assertNotIn("2026-03-19_1015", output)

    def test_spark_rm_removes_audio_transcript_and_spark_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            with working_directory(repo_root):
                spark_id = "2026-03-19_0900"
                self.write_spark_bundle(
                    spark_id,
                    transcript="Delete me",
                    sparks=[{"spark": "Deletion seam"}],
                )

                output = self.run_cli(["spark", "rm", spark_id])

                self.assertIn(f"Removed spark {spark_id}", output)
                self.assertFalse(Path(f"data/scintilla/audio/{spark_id}.wav").exists())
                self.assertFalse(
                    Path(f"data/scintilla/transcripts/{spark_id}.txt").exists()
                )
                self.assertFalse(Path(f"data/scintilla/sparks/{spark_id}.json").exists())


if __name__ == "__main__":
    unittest.main()
