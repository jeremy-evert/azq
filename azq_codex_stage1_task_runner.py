#!/usr/bin/env python3
"""AZQ Codex task runner and reporter for staged AZQ build waves."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


DEFAULT_STAGE = 1
DEFAULT_WAVE = "wave_a"
DEFAULT_TEMPLATE_FILE = "AZQ_CODEX_PROMPT_TEMPLATE_STAGE_1.md"
DEFAULT_REPORT_FILE = "codex_reports/codex_azq_task_status_report.md"
DEFAULT_MAX_ATTEMPTS = 3
TASKS_FILE_GLOB = "AZQ_BUILD_TASKS_STAGE_*_WAVE_*.json"
TASKS_FILE_PATTERN = re.compile(r"^AZQ_BUILD_TASKS_STAGE_(\d+)_(WAVE_[A-Z0-9_]+)\.json$")
CHECKS_FILE_GLOB = "AZQ_CHECKS_STAGE_*_WAVE_*.json"
CHECKS_FILE_PATTERN = re.compile(r"^AZQ_CHECKS_STAGE_(\d+)_(WAVE_[A-Z0-9_]+)\.json$")


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


@dataclass
class WavePaths:
    stage: int
    wave: str
    tasks_file: str
    checks_file: str
    state_file: str
    runs_dir: str


@dataclass
class TaskSummary:
    task_id: str
    title: str
    raw_status: str
    normalized_status: str
    updated_at: str
    note: str


@dataclass
class WaveSummary:
    stage: int
    wave: str
    tasks_file: str
    state_file: str
    checks_file: str
    runs_dir: str
    tasks_present: int
    counts: Dict[str, int]
    tasks: List[TaskSummary]
    warnings: List[str]


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


def load_checks_recipe(checks_file: Path) -> Dict[str, Any]:
    data = read_json(checks_file)
    if not isinstance(data, dict):
        raise ValueError(f"Checks file must contain a JSON object: {checks_file}")
    return data


def is_task_manifest(data: Any) -> bool:
    if not isinstance(data, list):
        return False
    return all(isinstance(item, dict) and "task_id" in item for item in data)


def task_manifest_exists(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        return is_task_manifest(read_json(path))
    except (OSError, json.JSONDecodeError, ValueError):
        return False


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
    task_json = json.dumps(task, indent=2, ensure_ascii=False)

    filled = template.replace(
        "Task object:\n[paste one JSON task here]",
        f"Task object:\n{task_json}",
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
    checks_file: Optional[Path],
    metadata: Dict[str, Any],
    workspace: Path,
) -> None:
    attempt_dir.mkdir(parents=True, exist_ok=True)
    (attempt_dir / "prompt.txt").write_text(prompt, encoding="utf-8")
    write_json(attempt_dir / "metadata.json", metadata)
    write_json(
        attempt_dir / "checks_recipe_snapshot.json",
        {"checks_file": str(checks_file) if checks_file is not None else "", "checks": check_specs, "human_checks": human_checks},
    )

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


def normalize_wave_name(raw_wave: str) -> str:
    wave = raw_wave.strip().lower().replace("-", "_")
    if not wave.startswith("wave_"):
        raise ValueError(f"Wave must look like wave_a, wave_b, etc.: {raw_wave}")
    if not re.fullmatch(r"wave_[a-z0-9_]+", wave):
        raise ValueError(f"Unsupported wave format: {raw_wave}")
    return wave


def wave_upper_token(wave: str) -> str:
    return normalize_wave_name(wave).upper()


def normalize_stage_number(raw_stage: int | str) -> int:
    try:
        stage = int(raw_stage)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Stage must be an integer like 1 or 2: {raw_stage}") from exc
    if stage < 1:
        raise ValueError(f"Stage must be >= 1: {raw_stage}")
    return stage


def derive_wave_paths(wave: str, stage: int | str = DEFAULT_STAGE) -> WavePaths:
    stage_number = normalize_stage_number(stage)
    normalized = normalize_wave_name(wave)
    upper = wave_upper_token(normalized)
    return WavePaths(
        stage=stage_number,
        wave=normalized,
        tasks_file=f"AZQ_BUILD_TASKS_STAGE_{stage_number}_{upper}.json",
        checks_file=f"AZQ_CHECKS_STAGE_{stage_number}_{upper}.json",
        state_file=f".azq_codex_progress_stage{stage_number}_{normalized}.json",
        runs_dir=f".azq_codex_runs/stage{stage_number}_{normalized}",
    )


def normalize_task_status(raw_status: Optional[str]) -> str:
    if raw_status in {None, "", "todo"}:
        return "pending"
    if raw_status in {"passed_checks", "committed"}:
        return "done"
    if raw_status == "blocked":
        return "failed"
    if raw_status in {"in_progress", "codex_submitted", "repair_loop"}:
        return "active"
    return "unknown"


def wave_sort_key(paths: WavePaths) -> tuple[int, str]:
    return paths.stage, paths.wave


def discover_stage_waves(workspace: Path) -> List[WavePaths]:
    discovered: Dict[str, WavePaths] = {}
    for tasks_file in sorted(workspace.glob(TASKS_FILE_GLOB)):
        match = TASKS_FILE_PATTERN.match(tasks_file.name)
        if not match:
            continue
        stage, wave = match.groups()
        wave_paths = derive_wave_paths(wave.lower(), stage)
        discovered[f"stage{wave_paths.stage}:{wave_paths.wave}"] = wave_paths

    for checks_file in sorted(workspace.glob(CHECKS_FILE_GLOB)):
        match = CHECKS_FILE_PATTERN.match(checks_file.name)
        if not match:
            continue
        stage, wave = match.groups()
        wave_paths = derive_wave_paths(wave.lower(), stage)
        key = f"stage{wave_paths.stage}:{wave_paths.wave}"
        if key in discovered:
            continue
        if task_manifest_exists(checks_file):
            discovered[key] = wave_paths

    return sorted(discovered.values(), key=wave_sort_key)


def discover_stage1_waves(workspace: Path) -> List[WavePaths]:
    return [paths for paths in discover_stage_waves(workspace) if paths.stage == 1]


def resolve_manifest_paths(
    workspace: Path,
    wave_paths: WavePaths,
    tasks_override: Optional[str],
    checks_override: Optional[str],
) -> tuple[Path, Optional[Path], List[str]]:
    warnings: List[str] = []
    tasks_file = (workspace / (tasks_override or wave_paths.tasks_file)).resolve()
    checks_file: Optional[Path] = (workspace / (checks_override or wave_paths.checks_file)).resolve()

    if tasks_override or tasks_file.exists():
        return tasks_file, checks_file, warnings

    if checks_override:
        return tasks_file, checks_file, warnings

    if checks_file is not None and task_manifest_exists(checks_file):
        warnings.append(
            f"Using {checks_file.name} as the task manifest for {wave_paths.wave} because {tasks_file.name} is missing."
        )
        warnings.append(f"No standalone checks recipe found for {wave_paths.wave}; automated checks are disabled for this wave.")
        return checks_file, None, warnings

    return tasks_file, checks_file, warnings


def summarize_wave(paths: WavePaths, workspace: Path) -> WaveSummary:
    tasks_path, checks_path, warnings = resolve_manifest_paths(workspace, paths, None, None)
    state_path = (workspace / paths.state_file).resolve()
    tasks = load_tasks(tasks_path)
    state = load_state(state_path)
    task_state = state.get("tasks", {})

    if not state_path.exists():
        warnings.append(f"Missing state file: {state_path.name}; tasks without entries are treated as pending.")
    if checks_path is None:
        warnings.append(f"Checks disabled for {paths.wave}; no standalone checks recipe was resolved.")
    elif not checks_path.exists():
        warnings.append(f"Missing checks file: {checks_path.name}.")

    counts = {"done": 0, "pending": 0, "failed": 0, "active": 0, "unknown": 0}
    task_summaries: List[TaskSummary] = []
    for task in tasks:
        task_id = str(task.get("task_id", ""))
        entry = task_state.get(task_id, {})
        raw_status = str(entry.get("status", "todo")) if entry else "todo"
        normalized_status = normalize_task_status(raw_status)
        counts[normalized_status] += 1
        task_summaries.append(
            TaskSummary(
                task_id=task_id,
                title=str(task.get("title", "")),
                raw_status=raw_status,
                normalized_status=normalized_status,
                updated_at=str(entry.get("updated_at", "")),
                note=str(entry.get("note", "")),
            )
        )

    return WaveSummary(
        stage=paths.stage,
        wave=paths.wave,
        tasks_file=tasks_path.name,
        state_file=paths.state_file,
        checks_file=checks_path.name if checks_path is not None else "(none)",
        runs_dir=paths.runs_dir,
        tasks_present=len(tasks),
        counts=counts,
        tasks=task_summaries,
        warnings=warnings,
    )


def render_markdown_report(summaries: List[WaveSummary], workspace: Path) -> str:
    generated_at = now_iso()
    combined = {"done": 0, "pending": 0, "failed": 0, "active": 0, "unknown": 0}
    total_tasks = 0

    for summary in summaries:
        total_tasks += summary.tasks_present
        for key in combined:
            combined[key] += summary.counts[key]

    lines: List[str] = [
        "# AZQ Task Status Report",
        "",
        f"Generated: {generated_at}",
        f"Workspace: `{workspace}`",
        "",
        "## Combined counts",
        "",
        f"- Done: {combined['done']}",
        f"- Pending: {combined['pending']}",
        f"- Failed: {combined['failed']}",
        f"- Active: {combined['active']}",
        f"- Unknown: {combined['unknown']}",
        f"- Total: {total_tasks}",
        "",
        "## Per-wave summary",
        "",
        "| Stage | Wave | Done | Pending | Failed | Active | Unknown | Total |",
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]

    for summary in summaries:
        lines.append(
            f"| {summary.stage} | `{summary.wave}` | {summary.counts['done']} | {summary.counts['pending']} | "
            f"{summary.counts['failed']} | {summary.counts['active']} | {summary.counts['unknown']} | {summary.tasks_present} |"
        )

    for summary in summaries:
        lines.extend(
            [
                "",
                f"## stage{summary.stage}_{summary.wave}",
                "",
                f"- Tasks file: `{summary.tasks_file}`",
                f"- State file: `{summary.state_file}`",
                f"- Checks file: `{summary.checks_file}`",
                f"- Runs dir: `{summary.runs_dir}`",
                f"- Counts: done={summary.counts['done']}, pending={summary.counts['pending']}, failed={summary.counts['failed']}, active={summary.counts['active']}, unknown={summary.counts['unknown']}",
            ]
        )
        if summary.warnings:
            lines.append("- Warnings:")
            for warning in summary.warnings:
                lines.append(f"  - {warning}")
        lines.extend(
            [
                "",
                "| Task ID | Status | Raw status | Updated | Note | Title |",
                "| --- | --- | --- | --- | --- | --- |",
            ]
        )
        for task in summary.tasks:
            updated = task.updated_at or "-"
            note = task.note or "-"
            title = task.title.replace("|", "\\|")
            lines.append(
                f"| `{task.task_id}` | `{task.normalized_status}` | `{task.raw_status}` | {updated} | {note} | {title} |"
            )

    lines.append("")
    return "\n".join(lines)


def write_status_report(workspace: Path, output: str) -> Path:
    report_path = (workspace / output).resolve()
    summaries = [summarize_wave(paths, workspace) for paths in discover_stage_waves(workspace)]
    markdown = render_markdown_report(summaries, workspace)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(markdown, encoding="utf-8")
    return report_path


def render_stage_closeout_message(stage: int) -> str:
    return f"Stage {normalize_stage_number(stage)} Complete."


def resolve_run_paths(args: argparse.Namespace) -> tuple[WavePaths, Path, Path, Path, Optional[Path], Path, Path, List[str]]:
    workspace = Path(args.workspace).resolve()
    wave_paths = derive_wave_paths(args.wave, args.stage)
    tasks_file, checks_file, warnings = resolve_manifest_paths(workspace, wave_paths, args.tasks_file, args.checks_file)
    template_file = (workspace / args.prompt_template).resolve()
    state_file = (workspace / (args.state_file or wave_paths.state_file)).resolve()
    runs_dir = (workspace / (args.runs_dir or wave_paths.runs_dir)).resolve()
    return wave_paths, workspace, tasks_file, template_file, checks_file, state_file, runs_dir, warnings


def run_mode(args: argparse.Namespace) -> int:
    _, workspace, tasks_file, template_file, checks_file, state_file, runs_dir, path_warnings = resolve_run_paths(args)
    persist_state = not args.dry_run

    tasks = load_tasks(tasks_file)
    checks_recipe: Dict[str, Any] = {}
    for warning in path_warnings:
        print(f"Warning: {warning}", file=sys.stderr)
    if checks_file is not None and checks_file.exists():
        checks_recipe = load_checks_recipe(checks_file)
    else:
        missing = str(checks_file) if checks_file is not None else f"{args.wave} (no checks recipe)"
        print(f"Warning: checks file not found, continuing with no automated checks: {missing}", file=sys.stderr)

    state = load_state(state_file)
    try:
        task = choose_next_task(tasks, state, args.task_id)
    except ValueError as exc:
        if str(exc) != "No remaining tasks found.":
            raise
        report_path = write_status_report(workspace, DEFAULT_REPORT_FILE)
        print(f"No remaining tasks found in stage {args.stage} {args.wave}.")
        print(f"Wrote report: {report_path}")
        print(render_stage_closeout_message(args.stage))
        return 0
    task_id = task["task_id"]
    task_slug = safe_task_slug(task_id)

    recipe_retry_cap = checks_recipe.get("defaults", {}).get("retry_cap")
    max_attempts = int(recipe_retry_cap) if recipe_retry_cap is not None else int(args.max_attempts)

    if persist_state:
        update_task_state(state, task_id, "in_progress")
        state.setdefault("history", []).append({"event": "start_task", "task_id": task_id, "at": now_iso()})
        save_state(state_file, state)

    original_prompt = build_original_prompt(template_file, task)
    prompt = original_prompt
    task_runs_dir = runs_dir / task_slug
    task_runs_dir.mkdir(parents=True, exist_ok=True)

    last_checks: List[CheckResult] = []
    for attempt in range(1, max_attempts + 1):
        attempt_prefix = "dry_run" if args.dry_run else "attempt"
        attempt_dir = task_runs_dir / f"{attempt_prefix}_{attempt:02d}"
        if persist_state:
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
            "stage": args.stage,
            "wave": args.wave,
            "checks_file": str(checks_file) if checks_file is not None else "",
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
            if persist_state:
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
            if persist_state:
                update_task_state(state, task_id, "repair_loop", note=f"attempt {attempt} failed")
                state.setdefault("history", []).append({"event": "repair_loop", "task_id": task_id, "attempt": attempt, "at": now_iso()})
                save_state(state_file, state)
            prompt = build_repair_prompt(original_prompt, failed_checks_text(checks))
            continue

        if persist_state:
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


def report_mode(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    report_path = write_status_report(workspace, args.output)
    print(f"Wrote report: {report_path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run and report AZQ Codex task waves.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run one task from the selected stage and wave.")
    run_parser.add_argument("--workspace", default=".", help="Repository root to run inside.")
    run_parser.add_argument("--stage", type=int, default=DEFAULT_STAGE, help="Task stage to run, for example 1 or 2.")
    run_parser.add_argument("--wave", default=DEFAULT_WAVE, help="Task wave to run, for example wave_a or wave_b.")
    run_parser.add_argument("--task-id", help="Specific task_id to run. Defaults to the first unfinished task in the selected wave.")
    run_parser.add_argument("--tasks-file", help="Override the derived tasks file for the selected wave.")
    run_parser.add_argument("--prompt-template", default=DEFAULT_TEMPLATE_FILE)
    run_parser.add_argument("--checks-file", help="Override the derived checks file for the selected wave.")
    run_parser.add_argument("--state-file", help="Override the derived state file for the selected wave.")
    run_parser.add_argument("--runs-dir", help="Override the derived runs directory for the selected wave.")
    run_parser.add_argument("--max-attempts", type=int, default=DEFAULT_MAX_ATTEMPTS)
    run_parser.add_argument("--codex-bin", default="codex")
    run_parser.add_argument("--codex-extra", action="append", default=[], help="Extra argument to pass to `codex exec`. Repeat as needed.")
    run_parser.add_argument("--dry-run", action="store_true", help="Write prompt artifacts without invoking Codex.")
    run_parser.set_defaults(func=run_mode)

    report_parser = subparsers.add_parser("report", help="Scan staged wave manifests and write a markdown task status report.")
    report_parser.add_argument("--workspace", default=".", help="Repository root to inspect.")
    report_parser.add_argument("--output", default=DEFAULT_REPORT_FILE, help="Report path relative to the workspace root.")
    report_parser.set_defaults(func=report_mode)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        raise SystemExit(130)
