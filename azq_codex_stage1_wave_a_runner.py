#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


DEFAULT_STATE_FILE = ".azq_codex_progress_stage1_wave_a.json"
DEFAULT_RUNS_DIR = ".azq_codex_runs/stage1_wave_a"
DEFAULT_TASKS_FILE = "AZQ_BUILD_TASKS_STAGE_1_WAVE_A.json"
DEFAULT_TEMPLATE_FILE = "AZQ_CODEX_PROMPT_TEMPLATE_STAGE_1.md"
DEFAULT_MAX_ATTEMPTS = 3


@dataclass
class CheckResult:
    name: str
    command: str
    returncode: int
    stdout: str
    stderr: str

    @property
    def passed(self) -> bool:
        return self.returncode == 0


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def load_tasks(tasks_file: Path) -> List[Dict[str, Any]]:
    data = read_json(tasks_file)
    if not isinstance(data, list):
        raise ValueError(f"Tasks file must contain a JSON list: {tasks_file}")
    return data


def load_state(state_file: Path) -> Dict[str, Any]:
    if not state_file.exists():
        return {"tasks": {}, "history": []}
    return read_json(state_file)


def save_state(state_file: Path, state: Dict[str, Any]) -> None:
    write_json(state_file, state)


def extract_text_code_block(markdown: str) -> str:
    match = re.search(r"```text\n(.*?)```", markdown, flags=re.DOTALL)
    if match:
        return match.group(1).strip()
    match = re.search(r"```\n(.*?)```", markdown, flags=re.DOTALL)
    if match:
        return match.group(1).strip()
    return markdown.strip()


def build_original_prompt(template_file: Path, task: Dict[str, Any], add_conservative_line: bool = True) -> str:
    template_md = template_file.read_text(encoding="utf-8")
    template = extract_text_code_block(template_md)
    conservative = "\nDo not \"help\" by beginning the next task.\n" if add_conservative_line else ""
    return f"{template.rstrip()}\n{conservative}\nTask object:\n{json.dumps(task, indent=2, ensure_ascii=False)}\n"


def build_repair_prompt(original_prompt: str, failing_output: str) -> str:
    repair = (
        "\nYour previous patch did not satisfy the checks below.\n"
        "Revise only what is necessary to satisfy the task and the failing checks.\n"
        "Do not broaden scope.\n"
        "Do not begin the next task.\n\n"
        f"Failing checks:\n{failing_output.rstrip()}\n"
    )
    return f"{original_prompt.rstrip()}\n{repair}"


def choose_next_task(tasks: List[Dict[str, Any]], state: Dict[str, Any], explicit_task_id: Optional[str]) -> Dict[str, Any]:
    if explicit_task_id:
        for task in tasks:
            if task.get("task_id") == explicit_task_id:
                return task
        raise ValueError(f"Task id not found: {explicit_task_id}")

    task_state = state.get("tasks", {})
    for task in tasks:
        tid = task.get("task_id")
        status = task_state.get(tid, {}).get("status", "todo")
        if status not in {"committed", "passed_checks"}:
            return task
    raise ValueError("No remaining tasks found.")


def safe_task_slug(task_id: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", task_id)


def run_subprocess(cmd: List[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)


def run_shell(command: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=str(cwd), shell=True, capture_output=True, text=True)


def gather_git_snapshot(workspace: Path) -> Dict[str, str]:
    snapshots: Dict[str, str] = {}
    commands = {
        "git_status_short.txt": ["git", "status", "--short"],
        "git_diff_stat.txt": ["git", "diff", "--stat"],
        "git_diff.txt": ["git", "diff", "--no-ext-diff"],
    }
    for filename, cmd in commands.items():
        try:
            proc = run_subprocess(cmd, workspace)
            snapshots[filename] = proc.stdout + ("\n[stderr]\n" + proc.stderr if proc.stderr else "")
        except Exception as exc:
            snapshots[filename] = f"ERROR: {exc}\n"
    return snapshots


def wave_a_checks(task_id: str, workspace: Path) -> List[CheckResult]:
    checks: List[CheckResult] = []

    def add(name: str, command: str) -> None:
        proc = run_shell(command, workspace)
        checks.append(
            CheckResult(
                name=name,
                command=command,
                returncode=proc.returncode,
                stdout=proc.stdout,
                stderr=proc.stderr,
            )
        )

    add("compileall", "python -m compileall azq")

    storage_file = workspace / "azq" / "finis" / "storage.py"
    if task_id == "STAGE1-WAVEA-01":
        add("storage_file_exists", f"test -f {shlex.quote(str(storage_file))}")
        add("storage_import", "python -c \"import azq.finis.storage\"")
    else:
        add("storage_import", "python -c \"import azq.finis.storage\"")

    return checks


def checks_to_text(checks: List[CheckResult]) -> str:
    parts: List[str] = []
    for check in checks:
        status = "PASS" if check.passed else "FAIL"
        parts.append(
            f"[{status}] {check.name}\n"
            f"Command: {check.command}\n"
            f"Return code: {check.returncode}\n"
            f"--- stdout ---\n{check.stdout.rstrip()}\n"
            f"--- stderr ---\n{check.stderr.rstrip()}\n"
        )
    return "\n".join(parts).strip() + "\n"


def write_attempt_artifacts(attempt_dir: Path, *, prompt: str, response: subprocess.CompletedProcess[str] | None,
                            checks: List[CheckResult], metadata: Dict[str, Any], workspace: Path) -> None:
    attempt_dir.mkdir(parents=True, exist_ok=True)
    (attempt_dir / "prompt.txt").write_text(prompt, encoding="utf-8")
    write_json(attempt_dir / "metadata.json", metadata)
    if response is not None:
        (attempt_dir / "codex_stdout.txt").write_text(response.stdout, encoding="utf-8")
        (attempt_dir / "codex_stderr.txt").write_text(response.stderr, encoding="utf-8")
        write_json(
            attempt_dir / "codex_response.json",
            {"returncode": response.returncode, "stdout_len": len(response.stdout), "stderr_len": len(response.stderr)},
        )
    (attempt_dir / "checks.txt").write_text(checks_to_text(checks), encoding="utf-8")
    write_json(attempt_dir / "checks.json", [asdict(c) | {"passed": c.passed} for c in checks])
    for filename, contents in gather_git_snapshot(workspace).items():
        (attempt_dir / filename).write_text(contents, encoding="utf-8")


def failed_checks_text(checks: List[CheckResult]) -> str:
    failed = [c for c in checks if not c.passed]
    return checks_to_text(failed) if failed else ""


def update_task_state(state: Dict[str, Any], task_id: str, status: str, note: str = "") -> None:
    tasks = state.setdefault("tasks", {})
    entry = tasks.setdefault(task_id, {})
    entry["status"] = status
    entry["updated_at"] = now_iso()
    if note:
        entry["note"] = note


def codex_exec(prompt: str, workspace: Path, codex_bin: str, extra_args: List[str], dry_run: bool) -> Optional[subprocess.CompletedProcess[str]]:
    if dry_run:
        return None
    cmd = [codex_bin, "exec", *extra_args, prompt]
    return run_subprocess(cmd, workspace)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run AZQ Stage 1 Wave A Codex tasks with a bounded repair loop.")
    parser.add_argument("--workspace", default=".", help="Repository root to run inside.")
    parser.add_argument("--task-id", help="Specific task_id to run. Defaults to first unfinished task.")
    parser.add_argument("--tasks-file", default=DEFAULT_TASKS_FILE)
    parser.add_argument("--prompt-template", default=DEFAULT_TEMPLATE_FILE)
    parser.add_argument("--state-file", default=DEFAULT_STATE_FILE)
    parser.add_argument("--runs-dir", default=DEFAULT_RUNS_DIR)
    parser.add_argument("--max-attempts", type=int, default=DEFAULT_MAX_ATTEMPTS)
    parser.add_argument("--codex-bin", default="codex")
    parser.add_argument("--codex-extra", action="append", default=[], help="Extra argument to pass to `codex exec`. Repeat as needed.")
    parser.add_argument("--dry-run", action="store_true", help="Write prompt artifacts without invoking Codex.")
    args = parser.parse_args()

    workspace = Path(args.workspace).resolve()
    tasks_file = (workspace / args.tasks_file).resolve()
    template_file = (workspace / args.prompt_template).resolve()
    state_file = (workspace / args.state_file).resolve()
    runs_dir = (workspace / args.runs_dir).resolve()

    tasks = load_tasks(tasks_file)
    state = load_state(state_file)
    task = choose_next_task(tasks, state, args.task_id)
    task_id = task["task_id"]
    task_slug = safe_task_slug(task_id)

    update_task_state(state, task_id, "in_progress")
    state.setdefault("history", []).append({"event": "start_task", "task_id": task_id, "at": now_iso()})
    save_state(state_file, state)

    original_prompt = build_original_prompt(template_file, task)
    prompt = original_prompt
    task_runs_dir = runs_dir / task_slug
    task_runs_dir.mkdir(parents=True, exist_ok=True)

    last_checks: List[CheckResult] = []
    for attempt in range(1, args.max_attempts + 1):
        attempt_dir = task_runs_dir / f"attempt_{attempt:02d}"
        update_task_state(state, task_id, "codex_submitted", note=f"attempt {attempt}")
        save_state(state_file, state)

        response = codex_exec(prompt, workspace, args.codex_bin, args.codex_extra, args.dry_run)
        checks = wave_a_checks(task_id, workspace)
        last_checks = checks

        metadata = {
            "task_id": task_id,
            "attempt": attempt,
            "started_at": now_iso(),
            "dry_run": args.dry_run,
            "codex_command": None if args.dry_run else [args.codex_bin, "exec", *args.codex_extra, "<prompt elided>"] ,
        }
        write_attempt_artifacts(attempt_dir, prompt=prompt, response=response, checks=checks, metadata=metadata, workspace=workspace)

        failed = [c for c in checks if not c.passed]
        if not failed:
            update_task_state(state, task_id, "passed_checks", note=f"attempt {attempt}")
            state.setdefault("history", []).append({"event": "passed_checks", "task_id": task_id, "attempt": attempt, "at": now_iso()})
            save_state(state_file, state)
            print(f"Task {task_id} passed checks on attempt {attempt}.")
            print(f"Artifacts saved under: {attempt_dir}")
            return 0

        if attempt < args.max_attempts:
            update_task_state(state, task_id, "repair_loop", note=f"attempt {attempt} failed")
            state.setdefault("history", []).append({"event": "repair_loop", "task_id": task_id, "attempt": attempt, "at": now_iso()})
            save_state(state_file, state)
            prompt = build_repair_prompt(original_prompt, failed_checks_text(failed))
            continue

        update_task_state(state, task_id, "blocked", note=f"failed after {attempt} attempts")
        state.setdefault("history", []).append({"event": "blocked", "task_id": task_id, "attempt": attempt, "at": now_iso()})
        save_state(state_file, state)
        print(f"Task {task_id} failed checks after {attempt} attempts.")
        print(f"Inspect artifacts under: {attempt_dir}")
        print("\nFailed checks:\n")
        print(failed_checks_text(last_checks))
        return 1

    return 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        raise SystemExit(130)
