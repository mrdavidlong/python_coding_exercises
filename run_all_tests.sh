#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

cd "$ROOT_DIR/python_ds_algo"
pytest

cd "$ROOT_DIR/security_analytics_exercises"
pytest
