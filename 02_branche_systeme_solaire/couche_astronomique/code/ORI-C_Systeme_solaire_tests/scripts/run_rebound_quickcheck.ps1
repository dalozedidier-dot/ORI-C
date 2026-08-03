$ErrorActionPreference = "Stop"
python -m pip install -e ".[dev,nbody]"
python -m oric_solar_history doctor
python -m oric_solar_history run --config configs/rebound_quickcheck.yaml --overwrite
