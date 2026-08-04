.PHONY: test integrity manifest maximum maximum-tests

test:
	python scripts/valider_tout.py

integrity:
	python verifier_dossier.py

manifest:
	python build_manifest.py build

maximum:
	python plan_directeur/campagne_maximale_trois_branches/run_all.py

maximum-tests:
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q plan_directeur/campagne_maximale_trois_branches/tests
