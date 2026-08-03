.PHONY: install test smoke all catalog report
install:
	python -m pip install -e .

test:
	python -m pytest

catalog:
	python scripts/build_catalog.py

smoke:
	PYTHONPATH=src python -m oric_full smoke

all:
	PYTHONPATH=src python -m oric_full run --all --allow-missing-data

report:
	PYTHONPATH=src python -m oric_full report results/latest
