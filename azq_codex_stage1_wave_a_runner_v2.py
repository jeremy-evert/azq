#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
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
DEFAULT_CHECKS_FILE = "AZQ_CHECKS_STAGE_1_WAVE_A.json"
DEFAULT_MAX_ATTEMPTS = 3


@dataclass
class CheckResult:
    name: str
    check_type: str
    required: bool
    command: str
    returncode: int
    stdout: str
    stderr: str
    description: str = ""

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
    conservative = '\nDo not "help" by beginning the next task.\n' if add_conservative_line else ""
    task_json = json.dumps(task, indent=2, ensure_ascii=False)

    filled = template.replace(
        "Task object:\n[paste one JSON task here]",
        f'Task object:\n{task_json}'
    )

    if add_conservative_line:
        filled = filled.replace(
            "Task object:\n",
            'Do not "help" by beginning the next task.\n\nTask object:\n',
            1,
        )

    return filled.rstrip() + "\n"


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


def load_checks_recipe(checks_file: Path) -> Dict[str, Any]:
    data = read_json(checks_file)
    if not isinstance(data, dict):
        raise ValueError(f"Checks file must contain a JSON object: {checks_file}")
    return data


def merged_checks_for_task(recipe: Dict[str, Any], task_id: str) -> tuple[list[dict[str, Any]], list[str]]:
    defaults = recipe.get("defaults", {})
    baseline_checks = defaults.get("baseline_checks", [])
    tasks = recipe.get("tasks", {})
    task_entry = tasks.get(task_id, {})
    task_checks = task_entry.get("checks", [])
    human_checks = task_entry.get("human_checks", [])
    merged = list(baseline_checks) + list(task_checks)
    return merged, list(human_checks)


def execute_check(spec: Dict[str, Any], workspace: Path) -> CheckResult:
    name = spec.get("name", "unnamed_check")
    check_type = spec.get("type", "shell")
    required = bool(spec.get("required", True))
    description = spec.get("description", "")

    if check_type == "shell":
        command = spec["command"]
        proc = run_shell(command, workspace)
        return CheckResult(
            name=name,
            check_type=check_type,
            required=required,
            command=command,
            returncode=proc.returncode,
            stdout=proc.stdout,
            stderr=proc.stderr,
            description=description,
        )

    if check_type == "python":
        code = spec["code"]
        command = f"{sys.executable} -c <python check>"
        proc = run_subprocess([sys.executable, "-c", code], workspace)
        return CheckResult(
            name=name,
            check_type=check_type,
            required=required,
            command=command,
            returncode=proc.returncode,
            stdout=proc.stdout,
            stderr=proc.stderr,
            description=description,
        )

    raise ValueError(f"Unsupported check type: {check_type}")


def run_recipe_checks(task_id: str, workspace: Path, checks_recipe: Dict[str, Any]) -> tuple[list[CheckResult], list[str], list[dict[str, Any]]]:
    specs, human_checks = merged_checks_for_task(checks_recipe, task_id)
    results = [execute_check(spec, workspace) for spec in specs]
    return results, human_checks, specs


def checks_to_text(checks: List[CheckResult]) -> str:
    parts: List[str] = []
    for check in checks:
        status = "PASS" if check.passed else "FAIL"
        desc = f"Description: {check.description}\n" if check.description else ""
        parts.append(
            f"[{status}] {check.name}\n"
            f"{desc}"
            f"Type: {check.check_type}\n"
            f"Required: {check.required}\n"
            f"Command: {check.command}\n"
            f"Return code: {check.returncode}\n"
            f"--- stdout ---\n{check.stdout.rstrip()}\n"
            f"--- stderr ---\n{check.stderr.rstrip()}\n"
        )
    return "\n".join(parts).strip() + "\n"


def failed_checks_text(checks: List[CheckResult]) -> str:
    failed = [c for c in checks if c.required and not c.passed]
    return checks_to_text(failed) if failed else ""


def write_attempt_artifacts(
    attempt_dir: Path,
    *,
    prompt: str,
    response: subprocess.CompletedProcess[str] | None,
    checks: List[CheckResult],
    human_checks: List[str],
    check_specs: List[dict[str, Any]],
    checks_file: Path,
    metadata: Dict[str, Any],
    workspace: Path,
) -> None:
    attempt_dir.mkdir(parents=True, exist_ok=True)
    (attempt_dir / "prompt.txt").write_text(prompt, encoding="utf-8")
    write_json(attempt_dir / "metadata.json", metadata)
    write_json(attempt_dir / "checks_recipe_snapshot.json", {"checks_file": str(checks_file), "checks": check_specs, "human_checks": human_checks})

    if response is not None:
        (attempt_dir / "codex_stdout.txt").write_text(response.stdout, encoding="utf-8")
        (attempt_dir / "codex_stderr.txt").write_text(response.stderr, encoding="utf-8")
        write_json(
            attempt_dir / "codex_response.json",
            {"returncode": response.returncode, "stdout_len": len(response.stdout), "stderr_len": len(response.stderr)},
        )

    (attempt_dir / "checks.txt").write_text(checks_to_text(checks), encoding="utf-8")
    write_json(attempt_dir / "checks.json", [asdict(c) | {"passed": c.passed} for c in checks])

    human_text = ""
    if human_checks:
        human_text = "\n".join(f"- {item}" for item in human_checks) + "\n"
    (attempt_dir / "human_checks.txt").write_text(human_text, encoding="utf-8")
    write_json(attempt_dir / "human_checks.json", human_checks)

    for filename, contents in gather_git_snapshot(workspace).items():
        (attempt_dir / filename).write_text(contents, encoding="utf-8")


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


def has_required_failures(checks: List[CheckResult]) -> bool:
    return any((not c.passed) and c.required for c in checks)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run AZQ Stage 1 Wave A Codex tasks with a bounded repair loop.")
    parser.add_argument("--workspace", default=".", help="Repository root to run inside.")
    parser.add_argument("--task-id", help="Specific task_id to run. Defaults to first unfinished task.")
    parser.add_argument("--tasks-file", default=DEFAULT_TASKS_FILE)
    parser.add_argument("--prompt-template", default=DEFAULT_TEMPLATE_FILE)
    parser.add_argument("--checks-file", default=DEFAULT_CHECKS_FILE)
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
    checks_file = (workspace / args.checks_file).resolve()
    state_file = (workspace / args.state_file).resolve()
    runs_dir = (workspace / args.runs_dir).resolve()

    tasks = load_tasks(tasks_file)
    checks_recipe = load_checks_recipe(checks_file)
    state = load_state(state_file)
    task = choose_next_task(tasks, state, args.task_id)
    task_id = task["task_id"]
    task_slug = safe_task_slug(task_id)

    recipe_retry_cap = checks_recipe.get("defaults", {}).get("retry_cap")
    max_attempts = int(recipe_retry_cap) if recipe_retry_cap is not None else int(args.max_attempts)

    update_task_state(state, task_id, "in_progress")
    state.setdefault("history", []).append({"event": "start_task", "task_id": task_id, "at": now_iso()})
    save_state(state_file, state)

    original_prompt = build_original_prompt(template_file, task)
    prompt = original_prompt
    task_runs_dir = runs_dir / task_slug
    task_runs_dir.mkdir(parents=True, exist_ok=True)

    last_checks: List[CheckResult] = []
    for attempt in range(1, max_attempts + 1):
        attempt_dir = task_runs_dir / f"attempt_{attempt:02d}"
        update_task_state(state, task_id, "codex_submitted", note=f"attempt {attempt}")
        save_state(state_file, state)

        response = codex_exec(prompt, workspace, args.codex_bin, args.codex_extra, args.dry_run)
        checks, human_checks, check_specs = run_recipe_checks(task_id, workspace, checks_recipe)
        last_checks = checks

        metadata = {
            "task_id": task_id,
            "attempt": attempt,
            "started_at": now_iso(),
            "dry_run": args.dry_run,
            "checks_file": str(checks_file),
            "codex_command": None if args.dry_run else [args.codex_bin, "exec", *args.codex_extra, "<prompt elided>"],
        }
        write_attempt_artifacts(
            attempt_dir,
            prompt=prompt,
            response=response,
            checks=checks,
            human_checks=human_checks,
            check_specs=check_specs,
            checks_file=checks_file,
            metadata=metadata,
            workspace=workspace,
        )

        if not has_required_failures(checks):
            update_task_state(state, task_id, "passed_checks", note=f"attempt {attempt}")
            state.setdefault("history", []).append({"event": "passed_checks", "task_id": task_id, "attempt": attempt, "at": now_iso()})
            save_state(state_file, state)
            print(f"Task {task_id} passed checks on attempt {attempt}.")
            print(f"Artifacts saved under: {attempt_dir}")
            if human_checks:
                print("Human checks to review:")
                for item in human_checks:
                    print(f"- {item}")
            return 0

        if attempt < max_attempts:
            update_task_state(state, task_id, "repair_loop", note=f"attempt {attempt} failed")
            state.setdefault("history", []).append({"event": "repair_loop", "task_id": task_id, "attempt": attempt, "at": now_iso()})
            save_state(state_file, state)
            prompt = build_repair_prompt(original_prompt, failed_checks_text(checks))
            continue

        update_task_state(state, task_id, "blocked", note=f"failed after {attempt} attempts")
        state.setdefault("history", []).append({"event": "blocked", "task_id": task_id, "attempt": attempt, "at": now_iso()})
        save_state(state_file, state)
        print(f"Task {task_id} failed checks after {attempt} attempts.")
        print(f"Inspect artifacts under: {attempt_dir}")
        print("\nFailed required checks:\n")
        print(failed_checks_text(last_checks))
        if human_checks:
            print("Human checks to review once required failures are resolved:")
            for item in human_checks:
                print(f"- {item}")
        return 1

    return 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        raise SystemExit(130)
