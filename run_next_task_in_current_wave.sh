#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
WORKSPACE=${WORKSPACE:-$SCRIPT_DIR}
RUNNER="$WORKSPACE/azq_codex_stage1_task_runner.py"

select_current_wave() {
  (
    cd "$WORKSPACE"
    python - <<'PY'
from pathlib import Path

import azq_codex_stage1_task_runner as runner

workspace = Path.cwd()
unfinished = []

for paths in runner.discover_stage1_waves(workspace):
    summary = runner.summarize_wave(paths, workspace)
    remaining = (
        summary.counts["pending"]
        + summary.counts["failed"]
        + summary.counts["active"]
        + summary.counts["unknown"]
    )
    if remaining:
        unfinished.append(summary.wave)

print(unfinished[-1] if unfinished else "stage1_complete")
PY
  )
}

print_report() {
  python "$RUNNER" report --workspace "$WORKSPACE"

  echo
  echo "task status report"
  echo "=================="
  cat "$WORKSPACE/codex_reports/codex_azq_task_status_report.md"
}

print_wave_snapshot() {
  local wave="$1"

  (
    cd "$WORKSPACE"
    python - "$wave" <<'PY'
import sys
from pathlib import Path

import azq_codex_stage1_task_runner as runner

wave = sys.argv[1]
workspace = Path.cwd()
wave_paths = runner.derive_wave_paths(wave)
tasks_file, _checks_file, _warnings = runner.resolve_manifest_paths(workspace, wave_paths, None, None)
state_file = workspace / wave_paths.state_file

print()
print("wave snapshot")
print("=============")
print(f"wave: {wave}")
print(f"tasks file: {tasks_file.name}")
print(f"state file: {state_file.name}")

if state_file.exists():
    print()
    print(state_file.read_text(encoding="utf-8").rstrip())
else:
    print()
    print("(state file does not exist yet)")

print()
print(tasks_file.read_text(encoding="utf-8").rstrip())
PY
  )
}

print_suggested_commit_message() {
  local wave="$1"

  (
    cd "$WORKSPACE"
    python - "$wave" <<'PY'
import json
import sys
from pathlib import Path

import azq_codex_stage1_task_runner as runner

wave = sys.argv[1]
workspace = Path.cwd()
wave_paths = runner.derive_wave_paths(wave)
tasks_file, _checks_file, _warnings = runner.resolve_manifest_paths(workspace, wave_paths, None, None)
state_file = workspace / wave_paths.state_file

print()
print("suggested git commit message")
print("============================")

if not state_file.exists():
    print("No state file found.")
    raise SystemExit(0)

state = json.loads(state_file.read_text(encoding="utf-8"))
tasks = json.loads(tasks_file.read_text(encoding="utf-8"))

latest_pass = None
for event in state.get("history", []):
    if event.get("event") == "passed_checks":
        latest_pass = event

if latest_pass is None:
    print("No passed_checks event found.")
    raise SystemExit(0)

task_id = latest_pass.get("task_id")
task_map = {task.get("task_id"): task for task in tasks}
task = task_map.get(task_id)

if not task:
    print(f"No task definition found for {task_id}.")
    raise SystemExit(0)

message = task.get("suggested_commit_message", "(no suggested_commit_message found)")
print(f"{task_id}: {message}")
PY
  )
}

CURRENT_WAVE=$(select_current_wave)
RUN_STATUS=0

if [[ "$CURRENT_WAVE" == "stage1_complete" ]]; then
  echo "No remaining Stage 1 tasks."
  echo "Stage 1 Complete."
else
  echo "running next task in current wave: $CURRENT_WAVE"
  if ! python "$RUNNER" run --wave "$CURRENT_WAVE" --workspace "$WORKSPACE"; then
    RUN_STATUS=$?
  fi
fi

print_report

if [[ "$CURRENT_WAVE" != "stage1_complete" ]]; then
  print_wave_snapshot "$CURRENT_WAVE"
  print_suggested_commit_message "$CURRENT_WAVE"
fi

exit "$RUN_STATUS"
