#!/usr/bin/env sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
. "$ROOT/.venv/bin/activate"
oric-full import-existing "$ROOT/.." --data-dir "$ROOT/campagne_maximale_reelle/data"
oric-full run --all --real-data-only --data-dir "$ROOT/campagne_maximale_reelle/data" --output-dir "$ROOT/campagne_maximale_reelle/resultats_reproduits" --oric-root "$ROOT/.."
