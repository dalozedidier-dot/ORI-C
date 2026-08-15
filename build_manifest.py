"""Construit et vérifie le manifeste SHA-256 portable du dossier ORI-C.

Un pointeur Git LFS valide est inscrit avec l'OID et la taille du contenu réel,
pas avec l'empreinte du petit fichier pointeur. Le manifeste reste ainsi celui
de l'archive scientifique attendue même lorsqu'il est reconstruit depuis un
arbre source non hydraté.
"""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXCLUDED_PARTS = {
    ".git", "__pycache__", ".pytest_cache", ".pytest-tmp",
    ".mplconfig", ".claude", "node_modules", "dist",
}
EXCLUDED_ROOT_FILES = {"MANIFEST.sha256", "MANIFEST.sha256.json"}
EXCLUDED_PATH_PREFIXES = ("donnees_externes/lot_scientifique_maximal_2026_08_05/raw/",)
CANONICAL_NUMBERS = ROOT / "preuves/CHIFFRES.json"
LFS_PATTERN = re.compile(
    rb"\Aversion https://git-lfs\.github\.com/spec/v1\n"
    rb"oid sha256:([0-9a-f]{64})\n"
    rb"size ([0-9]+)\n?\Z"
)


def ignored_by_git() -> set[str]:
    """Chemins que `.gitignore` écarte, s'il y a un dépôt Git.

    Le manifeste décrit ce qu'un clonage restituera. Un fichier ignoré par Git
    est présent sur le disque du rédacteur et absent partout ailleurs : l'inscrire
    fait passer le contrôle en local et échouer après le `push`.

    La sortie est lue en NUL-séparé avec `core.quotepath=false` : sans cela git
    échappe les caractères non ASCII en octal et le chemin ne correspond plus au
    fichier réel.
    """
    try:
        sortie = subprocess.run(
            ["git", "-c", "core.quotepath=false", "ls-files", "--others",
             "--ignored", "--exclude-standard", "-z"],
            cwd=ROOT, capture_output=True, check=True,
        ).stdout.decode("utf-8", "surrogateescape")
    except (OSError, subprocess.CalledProcessError):
        return set()
    return {ligne.rstrip("/") for ligne in sortie.split(chr(0)) if ligne}


def _est_ignore(relatif: str, ignores: set[str]) -> bool:
    """Vrai si le chemin est ignoré, ou situé sous un dossier ignoré.

    `git ls-files --others --ignored` rend le dossier et non son contenu quand
    la règle porte sur un dossier entier. Comparer les seuls chemins de fichiers
    laisse alors entrer tout le contenu.
    """
    if relatif in ignores:
        return True
    return any(relatif.startswith(prefixe + "/") for prefixe in ignores)


def files() -> list[Path]:
    ignores = ignored_by_git()
    return sorted(
        (
            path for path in ROOT.rglob("*")
            if path.is_file()
            and path.relative_to(ROOT).as_posix() not in EXCLUDED_ROOT_FILES
            and not any(part in EXCLUDED_PARTS for part in path.relative_to(ROOT).parts)
            and not any(
                path.relative_to(ROOT).as_posix().startswith(prefix)
                for prefix in EXCLUDED_PATH_PREFIXES
            )
            and not _est_ignore(path.relative_to(ROOT).as_posix(), ignores)
        ),
        key=lambda path: path.relative_to(ROOT).as_posix(),
    )


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def lfs_metadata(path: Path) -> tuple[str, int] | None:
    if path.stat().st_size > 1024:
        return None
    data = path.read_bytes()
    match = LFS_PATTERN.fullmatch(data.replace(b"\r\n", b"\n"))
    if not match:
        return None
    return match.group(1).decode("ascii"), int(match.group(2))


def entry(path: Path) -> dict[str, object]:
    lfs = lfs_metadata(path)
    if lfs is None:
        sha256, size = digest(path), path.stat().st_size
        storage = "inline"
    else:
        sha256, size = lfs
        storage = "git-lfs"
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "size": size,
        "sha256": sha256,
        "storage": storage,
    }


def synchronize_manifest_file_count(count: int) -> None:
    """Synchronise le chiffre dérivé avant d'empreindre le registre.

    Le nombre de fichiers est une propriété du manifeste en cours de
    construction. Le maintenir manuellement désynchronisait CHIFFRES.json à
    chaque ajout de livrable et faisait échouer toutes les CI consommatrices.
    """
    if not CANONICAL_NUMBERS.is_file():
        return
    document = json.loads(CANONICAL_NUMBERS.read_text(encoding="utf-8"))
    item = next((value for value in document.get("valeurs", []) if value.get("id") == "MAIN_MANIFEST_FILES"), None)
    if item is None:
        raise SystemExit("Chiffre canonique MAIN_MANIFEST_FILES absent")
    item["value"] = count
    item["display"] = f"{count:,}".replace(",", " ")
    CANONICAL_NUMBERS.write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def build() -> list[dict[str, object]]:
    paths = files()
    synchronize_manifest_file_count(len(paths))
    entries = [entry(path) for path in paths]
    (ROOT / "MANIFEST.sha256").write_text(
        "".join(f"{item['sha256']}  {item['path']}\n" for item in entries),
        encoding="utf-8",
        newline="\n",
    )
    (ROOT / "MANIFEST.sha256.json").write_text(
        json.dumps(
            {
                "algorithm": "sha256",
                "path_base": ".",
                "lfs_policy": "OID and declared content size are recorded for valid Git LFS pointers",
                "files": entries,
            },
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return entries


def verify() -> None:
    document = json.loads((ROOT / "MANIFEST.sha256.json").read_text(encoding="utf-8"))
    expected = {item["path"]: item for item in document["files"]}
    actual = {path.relative_to(ROOT).as_posix(): path for path in files()}
    if set(expected) != set(actual):
        raise SystemExit("La liste de fichiers diffère du manifeste")
    for name, path in actual.items():
        current = entry(path)
        if (
            current["size"] != expected[name]["size"]
            or current["sha256"] != expected[name]["sha256"]
        ):
            raise SystemExit(f"Empreinte invalide : {name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("build", "verify"))
    args = parser.parse_args()
    if args.command == "build":
        entries = build()
        lfs_count = sum(item["storage"] == "git-lfs" for item in entries)
        print(f"{len(entries)} fichiers inscrits, dont {lfs_count} pointeurs Git LFS")
    else:
        verify()
        print("Manifeste valide")
