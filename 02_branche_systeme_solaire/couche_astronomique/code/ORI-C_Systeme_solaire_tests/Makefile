.PHONY: install test smoke doctor nbody-check verify clean

install:
	python -m pip install -r requirements.lock.txt
	python -m pip install --no-build-isolation --no-deps -e .

test:
	python -m compileall -q src tests
	python -m ruff check .
	python -m pytest

smoke:
	python -m oric_solar_history run --config configs/smoke_surrogate.yaml

doctor:
	python -m oric_solar_history doctor

nbody-check:
	python -m oric_solar_history run --config configs/rebound_quickcheck.yaml

verify: test smoke nbody-check

clean:
	rm -rf runs .pytest_cache .ruff_cache build dist
