#!/usr/bin/env bash
# setup.sh — bootstrap azq project

set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"

echo "[azq] Setting up environment..."

# 1. Ensure venv exists
if [ ! -d "$here/azq_env" ]; then
  echo "[azq] Creating virtual environment..."
  python3 -m venv "$here/azq_env"
fi

# 2. Activate venv
source "$here/azq_env/bin/activate"

# 3. Install dependencies
pip install --upgrade pip
pip install -r "$here/requirements.txt"

# 4. Check for .env
if [ ! -f "$here/.env" ]; then
  echo "[azq WARNING] No .env file found."
  echo "Create one with your API key, e.g.:"
  echo "  echo 'OPENAI_API_KEY=sk-xxxx' > $here/.env"
else
  echo "[azq] Found .env file."
fi

# 5. Test API key
python3 - <<'PY'
import os, sys
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    sys.exit("[azq ERROR] No API key found in environment or .env")

try:
    client = OpenAI(api_key=api_key)
    resp = client.models.list()
    print("[azq] ✅ API key works! Models available:", [m.id for m in resp.data[:3]], "...")
except Exception as e:
    sys.exit(f"[azq ERROR] API key check failed: {e}")
PY

echo "[azq] Setup complete."

