#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

python_exe="venv/bin/python"
if [ ! -x "$python_exe" ]; then
  python_exe="python"
fi

"$python_exe" -m uvicorn app.backend.main:app --host 127.0.0.1 --port 8000 --reload
