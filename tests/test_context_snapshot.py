# tests/test_context_snapshot.py
import pathlib
import re
from azq.context_snapshot import get_repo_context

def test_snapshot_includes_system_info():
    ctx = get_repo_context()
    assert "## System Info" in ctx
    assert "Python:" in ctx
    assert "OS:" in ctx

def test_snapshot_includes_git_info():
    ctx = get_repo_context()
    assert "## Git Commit" in ctx
    assert re.search(r"[0-9a-f]{7,40}", ctx), "Expected a git commit hash"
    assert "## Git Branch" in ctx
    assert "## Git Log" in ctx

def test_snapshot_includes_file_tree():
    ctx = get_repo_context()
    assert "## File Tree" in ctx
    # Your repo root should have at least these
    assert "README.md" in ctx or "ideas" in ctx

def test_snapshot_optional_files(tmp_path):
    # Fake a README + requirements
    (tmp_path / "README.md").write_text("Hello README")
    (tmp_path / "requirements.txt").write_text("pytest")

    cwd = pathlib.Path.cwd()
    try:
        # Temporarily chdir into tmp_path
        import os
        os.chdir(tmp_path)
        ctx = get_repo_context()
        assert "Hello README" in ctx
        assert "pytest" in ctx
    finally:
        os.chdir(cwd)

