#!/usr/bin/env sh
set -eu
rm -f '01_branche_matiere/hypergraphe_transformations/reclassement_relations.zip' 'LICENSE_PENDING.md'
cp "$(dirname "$0")/MANIFEST.sha256" MANIFEST.sha256
cp "$(dirname "$0")/MANIFEST.sha256.json" MANIFEST.sha256.json
python verifier_dossier.py
