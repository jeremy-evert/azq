# azq/context_snapshot.py
import subprocess, pathlib, platform, sys, os

def run(cmd: str, limit: int = None) -> str:
    """Run a shell command safely, return stdout or '' if it fails.
       Optionally limit to first N lines."""
    try:
        output = subprocess.check_output(cmd, shell=True, text=True).strip()
        if limit:
            return "\n".join(output.splitlines()[:limit])
        return output
    except Exception:
        return ""

def get_shell_history(limit=25) -> str:
    """Grab last N commands from shell history."""
    history_file = pathlib.Path.home() / ".bash_history"
    if history_file.exists():
        lines = history_file.read_text().splitlines()
        return "\n".join(lines[-limit:])
    return run(f"history | tail -n {limit}")

def get_repo_context() -> str:
    """Slimmed repo + system snapshot for azq ask.
    Keeps essentials without blowing token limits."""
    parts = []

    # --- System Information ---
    parts.append("## System Info")
    parts.append(f"OS: {platform.system()} {platform.release()}")
    parts.append(f"Arch: {platform.machine()}")
    parts.append(f"Python: {sys.version.split()[0]}")
    parts.append(f"Virtualenv: {os.environ.get('VIRTUAL_ENV', '(none)')}")
    parts.append("")

    # --- Installed packages (just 10 for context) ---
    parts.append("## Installed Packages (first 10)")
    parts.append(run("pip list --format=freeze", limit=10))

    # --- Git Information ---
    parts.append("\n## Git Commit")
    parts.append(run("git rev-parse HEAD"))

    parts.append("\n## Git Branch")
    parts.append(run("git rev-parse --abbrev-ref HEAD"))

    parts.append("\n## Git Log (last 2)")
    parts.append(run("git log -n 2 --oneline"))

    parts.append("\n## Git Diff (last commit)")
    diff = run("git diff HEAD~1..HEAD", limit=40)  # only 40 lines
    parts.append(diff if diff else "(no diff)")

    # --- File Tree (just top-level + 20 entries) ---
    parts.append("\n## File Tree (top level)")
    parts.append(run("ls -1 | head -n 20"))

    # --- README.md (first 50 lines) ---
    readme = pathlib.Path("README.md")
    if readme.exists():
        parts.append("\n## README.md (first 50 lines)")
        parts.append("\n".join(readme.read_text().splitlines()[:50]))

    # --- requirements.txt (first 20 lines) ---
    req = pathlib.Path("requirements.txt")
    if req.exists():
        parts.append("\n## requirements.txt (first 20 lines)")
        parts.append("\n".join(req.read_text().splitlines()[:20]))

    # --- Shell History ---
    parts.append("\n## Shell History (last 25)")
    parts.append(get_shell_history(limit=25))

    return "\n".join(parts)

