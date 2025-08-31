# azq/context_snapshot.py
import subprocess, pathlib

def run(cmd: str) -> str:
    """Run a shell command safely, return stdout or '' if it fails."""
    try:
        return subprocess.check_output(cmd, shell=True, text=True).strip()
    except Exception:
        return ""

def get_repo_context() -> str:
    """Collect repo state: commit hash, git diff, tree, README, requirements."""
    parts = []

    # Current commit hash
    parts.append("## Git Commit")
    parts.append(run("git rev-parse HEAD"))

    # Last commit log
    parts.append("\n## Git Log (last 3)")
    parts.append(run("git log -n 3 --oneline"))

    # Diff since last commit
    parts.append("\n## Git Diff")
    diff = run("git diff HEAD~1..HEAD")
    parts.append(diff if diff else "(no diff)")

    # File tree (depth 2 for readability)
    parts.append("\n## File Tree")
    parts.append(run("ls -R | head -n 200"))

    # README.md
    readme = pathlib.Path("README.md")
    if readme.exists():
        parts.append("\n## README.md")
        parts.append(readme.read_text())

    # requirements.txt
    req = pathlib.Path("requirements.txt")
    if req.exists():
        parts.append("\n## requirements.txt")
        parts.append(req.read_text())

    return "\n".join(parts)

