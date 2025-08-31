# azq/context_snapshot.py
import subprocess, pathlib, platform, sys, os

def run(cmd: str) -> str:
    """Run a shell command safely, return stdout or '' if it fails."""
    try:
        return subprocess.check_output(cmd, shell=True, text=True).strip()
    except Exception:
        return ""




# In azq/context_snapshot.py

def get_shell_history(limit=50) -> str:
    """Grab last N commands from shell history."""
    history_file = pathlib.Path.home() / ".bash_history"
    if history_file.exists():
        lines = history_file.read_text().splitlines()
        return "\n".join(lines[-limit:])
    # Fallback
    return run(f"history | tail -n {limit}")

def get_repo_context() -> str:
    """Collect repo + system state: commit, branch, diff, tree, README, reqs, system info."""
    parts = []
    # ... existing system + git info ...
    

    # --- System Information ---
    parts.append("## System Info")
    parts.append(f"OS: {platform.system()} {platform.release()} ({platform.version()})")
    parts.append(f"Arch: {platform.machine()}")
    parts.append(f"Python: {sys.version.split()[0]}")
    if os.environ.get("VIRTUAL_ENV"):
        parts.append(f"Virtualenv: {os.environ['VIRTUAL_ENV']}")
    else:
        parts.append("Virtualenv: (none)")
    parts.append("")

    # Installed packages (first 30 for brevity)
    parts.append("## Installed Packages (pip list --format=freeze | head -n 30)")
    parts.append(run("pip list --format=freeze | head -n 30"))

    # --- Git Information ---
    parts.append("\n## Git Commit")
    parts.append(run("git rev-parse HEAD"))

    parts.append("\n## Git Branch")
    parts.append(run("git rev-parse --abbrev-ref HEAD"))

    parts.append("\n## Git Log (last 3)")
    parts.append(run("git log -n 3 --oneline"))

    parts.append("\n## Git Diff")
    diff = run("git diff HEAD~1..HEAD")
    parts.append(diff if diff else "(no diff)")

    # --- File Tree ---
    parts.append("\n## File Tree (depth 2)")
    parts.append(run("ls -R | head -n 200"))

    # --- README.md ---
    readme = pathlib.Path("README.md")
    if readme.exists():
        parts.append("\n## README.md")
        parts.append(readme.read_text())

    # --- requirements.txt ---
    req = pathlib.Path("requirements.txt")
    if req.exists():
        parts.append("\n## requirements.txt")
        parts.append(req.read_text())

    # Shell history
    parts.append("\n## Shell History (last 200)")
    parts.append(get_shell_history())


    return "\n".join(parts)

