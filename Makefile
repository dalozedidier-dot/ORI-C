.PHONY: test integrity manifest

test:
	python scripts/valider_tout.py

integrity:
	python verifier_dossier.py

manifest:
	python build_manifest.py build
