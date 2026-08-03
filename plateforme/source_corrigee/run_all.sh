#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-travail_ORI-C}"
python -m pip install -e .
oric-full bootstrap "$WORKSPACE"
