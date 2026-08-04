$ErrorActionPreference = "Stop"
Remove-Item -LiteralPath "01_branche_matiere/hypergraphe_transformations/reclassement_relations.zip" -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath "LICENSE_PENDING.md" -Force -ErrorAction SilentlyContinue
Copy-Item -LiteralPath "$PSScriptRoot/MANIFEST.sha256" -Destination "MANIFEST.sha256" -Force
Copy-Item -LiteralPath "$PSScriptRoot/MANIFEST.sha256.json" -Destination "MANIFEST.sha256.json" -Force
python verifier_dossier.py
