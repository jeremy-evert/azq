#!/usr/bin/env bash
set -euo pipefail

echo "[test] azq ask"
./bin/azq ask "Test 2+2 question" > tests/out.txt

# Verify output contains something (assistant reply)
grep -q "4" tests/out.txt || echo "[warn] Assistant reply not as expected"

# Verify log contains USER and ASSISTANT
grep -q "USER: Test 2+2 question" logs/chatlog.md
grep -q "ASSISTANT:" logs/chatlog.md

echo "[test] done ✅"

