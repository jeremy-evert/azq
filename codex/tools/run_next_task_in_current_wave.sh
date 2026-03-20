#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
WORKSPACE=${WORKSPACE:-$(cd "$SCRIPT_DIR/../.." && pwd)}
RUNNER="$WORKSPACE/codex/tools/azq_codex_task_runner.py"

section() {
  echo
  echo "$1"
  printf '%*s\n' "${#1}" '' | tr ' ' '='
}

select_current_wave() {
  (
    cd "$WORKSPACE"
    python - <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "codex" / "tools"))
import azq_codex_task_runner as runner

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

  section "task status report"
  cat "$WORKSPACE/codex/reports/codex_azq_task_status_report.md"
}

print_wave_snapshot() {
  local stage="$1"
  local wave="$2"

  (
    cd "$WORKSPACE"
    python - "$stage" "$wave" <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "codex" / "tools"))
import azq_codex_task_runner as runner

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
sys.path.insert(0, str(Path.cwd() / "codex" / "tools"))
import azq_codex_task_runner as runner

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

print_next_task_preview() {
  local stage="$1"
  local wave="$2"

  (
    cd "$WORKSPACE"
    python - "$stage" "$wave" <<'PY'
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "codex" / "tools"))
import azq_codex_task_runner as runner

stage = int(sys.argv[1])
wave = sys.argv[2]
workspace = Path.cwd()

wave_paths = runner.derive_wave_paths(wave, stage)
tasks_file, _checks_file, _warnings = runner.resolve_manifest_paths(workspace, wave_paths, None, None)
state_file = workspace / wave_paths.state_file

tasks = json.loads(tasks_file.read_text(encoding="utf-8"))
if state_file.exists():
    state = json.loads(state_file.read_text(encoding="utf-8"))
else:
    state = {"tasks": {}, "history": []}

try:
    task = runner.choose_next_task(tasks, state, None)
except ValueError as exc:
    if str(exc) != "No remaining tasks found.":
        raise
    print()
    print("next task preview")
    print("=================")
    print("No remaining tasks found in this wave.")
    print(f"{runner.render_stage_closeout_message(stage)}")
    raise SystemExit(0)

print()
print("next task preview")
print("=================")
print(f"task id: {task.get('task_id', '(unknown)')}")
print(f"title:   {task.get('title', '(no title)')}")
print(f"goal:    {task.get('goal', '(no goal)')}")
depends = task.get("depends_on", [])
print(f"depends: {', '.join(depends) if depends else '(none)'}")
PY
  )
}

print_git_summary() {
  section "git status"
  (
    cd "$WORKSPACE"
    git status --short || true
  )

  section "git diff stat"
  (
    cd "$WORKSPACE"
    git diff --stat || true
  )

  section "modified tracked files"
  (
    cd "$WORKSPACE"
    git diff --name-only || true
  )

  section "untracked files"
  (
    cd "$WORKSPACE"
    git ls-files --others --exclude-standard || true
  )
}

offer_git_add_patch() {
  local changed_files
  changed_files=$(cd "$WORKSPACE" && git diff --name-only)

  if [[ -z "$changed_files" ]]; then
    echo
    echo "No tracked file modifications to review with git add -p."
    return
  fi

  echo
  read -r -p "Launch interactive git add -p for tracked modified files? [y/N] " reply
  if [[ "$reply" =~ ^[Yy]$ ]]; then
    (
      cd "$WORKSPACE"
      while IFS= read -r file; do
        [[ -n "$file" ]] || continue
        echo
        echo "reviewing: $file"
        git add -p -- "$file"
      done <<< "$changed_files"
    )
  else
    echo "Skipping git add -p."
  fi
}

CURRENT_WAVE=$(select_current_wave)
RUN_STATUS=0

section "azq ritual runner"

if [[ "$CURRENT_WAVE" == "all_complete" ]]; then
  print_report
  echo
  echo "No remaining staged tasks."
  echo "Stage complete, confetti optional."
  exit 0
fi

CURRENT_STAGE=${CURRENT_WAVE%%:*}
CURRENT_WAVE_NAME=${CURRENT_WAVE#*:}

echo "running next task in current wave: stage $CURRENT_STAGE / $CURRENT_WAVE_NAME"

print_next_task_preview "$CURRENT_STAGE" "$CURRENT_WAVE_NAME"

START_TS=$(date '+%Y-%m-%d %H:%M:%S')
echo
echo "started: $START_TS"
echo "runner:  $RUNNER"
echo "workspace: $WORKSPACE"

set +e
python "$RUNNER" run --stage "$CURRENT_STAGE" --wave "$CURRENT_WAVE_NAME" --workspace "$WORKSPACE"
RUN_STATUS=$?
set -e

END_TS=$(date '+%Y-%m-%d %H:%M:%S')
echo
echo "finished: $END_TS"
echo "runner exit code: $RUN_STATUS"

print_report
print_wave_snapshot "$CURRENT_STAGE" "$CURRENT_WAVE_NAME"
print_suggested_commit_message "$CURRENT_STAGE" "$CURRENT_WAVE_NAME"
print_git_summary
offer_git_add_patch

exit "$RUN_STATUS"
