#!/usr/bin/env bash
set -euo pipefail

echo "[test] azq help"
./bin/azq help | grep -q "Usage: azq"

echo "[test] azq ask"
./bin/azq ask "Unit test question" 
grep -q "Unit test question" logs/chatlog.md

echo "[test] done ✅"

