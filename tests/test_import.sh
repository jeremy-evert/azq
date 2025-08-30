#!/usr/bin/env bash
set -euo pipefail

echo "[test] azq import"
./bin/azq import "https://example.com" 
ls logs/imported/convo-*.html > /dev/null

echo "[test] done ✅"

