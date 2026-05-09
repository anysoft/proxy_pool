#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

if [ -x ".venv/bin/python" ]; then
  PYTHON=".venv/bin/python"
else
  PYTHON="${PYTHON:-python3}"
fi

"$PYTHON" proxyPool.py server &
"$PYTHON" proxyPool.py schedule
