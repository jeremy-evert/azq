# tests/conftest.py
import os, tempfile, pathlib, pytest

@pytest.fixture
def clean_logs(tmp_path, monkeypatch):
    """Redirect logs/ to a temp dir for test isolation."""
    logdir = tmp_path / "logs"
    logdir.mkdir()
    monkeypatch.chdir(tmp_path)
    return logdir

