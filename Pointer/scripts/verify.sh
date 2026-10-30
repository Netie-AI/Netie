#!/usr/bin/env bash
# Linux/cloud verify. Does not install OpenClaw/Hermes on this VM.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
python3 scripts/verify_stack.py
