from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def main() -> int:
    gel = json.loads((HERE / "GEL_PALEO_HISTORY_01.json").read_text(encoding="utf-8"))
    divergences = []
    for nom, attendu in gel["fichiers"].items():
        reel = hashlib.sha256((HERE / nom).read_bytes()).hexdigest()
        if reel != attendu:
            divergences.append({"fichier": nom, "attendu": attendu, "reel": reel})
    if divergences:
        print(json.dumps(divergences, ensure_ascii=False, indent=2))
        return 1
    print("PALEO-HISTORY-01 : gel intact, 3 fichiers conformes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
