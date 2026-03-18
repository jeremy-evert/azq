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
for paths in runner.discover_stage_waves(workspace):
    summary = runner.summarize_wave(paths, workspace)
    remaining = (
        summary.counts["pending"]
        + summary.counts["failed"]
        + summary.counts["active"]
        + summary.counts["unknown"]
    )
    if remaining:
        print(f"{paths.stage}:{summary.wave}")
        break
else:
    print("all_complete")
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
  local stage="$1"
  local wave="$2"

  (
    cd "$WORKSPACE"
    python - "$stage" "$wave" <<'PY'
import sys
from pathlib import Path

import azq_codex_stage1_task_runner as runner

stage = int(sys.argv[1])
wave = sys.argv[2]
workspace = Path.cwd()
wave_paths = runner.derive_wave_paths(wave, stage)
tasks_file, _checks_file, _warnings = runner.resolve_manifest_paths(workspace, wave_paths, None, None)
state_file = workspace / wave_paths.state_file

print()
print("wave snapshot")
print("=============")
print(f"stage: {stage}")
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
  local stage="$1"
  local wave="$2"

  (
    cd "$WORKSPACE"
    python - "$stage" "$wave" <<'PY'
import json
import sys
from pathlib import Path

import azq_codex_stage1_task_runner as runner

stage = int(sys.argv[1])
wave = sys.argv[2]
workspace = Path.cwd()
wave_paths = runner.derive_wave_paths(wave, stage)
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

if [[ "$CURRENT_WAVE" == "all_complete" ]]; then
  print_report
  echo
  echo "No remaining staged tasks."
else
  CURRENT_STAGE=${CURRENT_WAVE%%:*}
  CURRENT_WAVE_NAME=${CURRENT_WAVE#*:}
  echo "running next task in current wave: stage $CURRENT_STAGE / $CURRENT_WAVE_NAME"
  set +e
  python "$RUNNER" run --stage "$CURRENT_STAGE" --wave "$CURRENT_WAVE_NAME" --workspace "$WORKSPACE"
  RUN_STATUS=$?
  set -e

  print_report
  print_wave_snapshot "$CURRENT_STAGE" "$CURRENT_WAVE_NAME"
  print_suggested_commit_message "$CURRENT_STAGE" "$CURRENT_WAVE_NAME"
fi

exit "$RUN_STATUS"
