#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="${project_dir}/src"
export MPLCONFIGDIR="${TMPDIR:-/tmp}/oric-memory-tests-matplotlib"

python3 -m oric_memory_tests \
  --root "${project_dir}" \
  run-all \
  --config configs/primary.json
