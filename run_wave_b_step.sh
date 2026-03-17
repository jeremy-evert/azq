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
