from pathlib import Path
import hashlib, json
HERE=Path(__file__).resolve().parent
PACKAGE_ROOT=HERE.parent
if (PACKAGE_ROOT/'data'/'campaign_exact').exists():
    ROOT=PACKAGE_ROOT
    DATA=ROOT/'data'/'campaign_exact'
    EXT=ROOT/'data'/'external'
    RESULTS=ROOT/'results'/'reproduced'
else:
    repo=None
    for p in [HERE,*HERE.parents]:
        if (p/'plateforme'/'campagne_maximale_reelle'/'data').is_dir():
            repo=p; break
    if repo is None:
        raise RuntimeError('Impossible de trouver les données ORI-C ou le paquet autonome')
    ROOT=repo
    DATA=repo/'plateforme'/'campagne_maximale_reelle'/'data'
    EXT=HERE.parent/'donnees_externes'
    RESULTS=HERE.parent/'resultats'
RESULTS.mkdir(parents=True, exist_ok=True)
SEED=20260816

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024), b''):
            h.update(b)
    return h.hexdigest()

def dump(name, obj):
    p=RESULTS/name
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    return p
