#!/usr/bin/env bash
set -e

python azq_codex_stage1_task_runner.py run --wave wave_b --workspace /data/git/azq
python azq_codex_stage1_task_runner.py report --workspace /data/git/azq

echo
echo "that is done, now here is the report."
echo "===================================="
cat codex_reports/codex_azq_task_status_report.md

echo
echo "check the homework"
echo "=================="
cat .azq_codex_progress_stage1_wave_b.json
echo
cat AZQ_BUILD_TASKS_STAGE_1_WAVE_B.json

echo
echo "suggested git commit message"
echo "============================"

python - <<'PY'
import json
from pathlib import Path

state_path = Path(".azq_codex_progress_stage1_wave_b.json")
tasks_path = Path("AZQ_BUILD_TASKS_STAGE_1_WAVE_B.json")

state = json.loads(state_path.read_text(encoding="utf-8"))
tasks = json.loads(tasks_path.read_text(encoding="utf-8"))

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
