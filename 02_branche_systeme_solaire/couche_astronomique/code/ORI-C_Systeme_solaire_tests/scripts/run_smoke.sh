#!/usr/bin/env bash
set -euo pipefail
python -m pip install -e '.[dev]'
pytest
python -m oric_solar_history run --config configs/smoke_surrogate.yaml --overwrite
