#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
if [[ ! -x .venv/bin/python ]]; then
  echo "Lancez d'abord : bash installer.sh"
  exit 1
fi
exec .venv/bin/python bot.py "$@"
