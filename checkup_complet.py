#!/usr/bin/env python3
"""Orchestrateur unique du méga check-up ORI-C.

Usage principal::

    python checkup_complet.py

Le script n'écrit aucun résultat de contrôle dans le dépôt. Les journaux et le
rapport sont placés hors de l'arbre ORI-C afin que le contrôle final du
manifeste puisse détecter toute dérive réellement produite par les recalculs.

Le fichier JSON ne contient que les chemins des données externes qui ne sont
pas versionnées dans le dépôt. Par défaut il est recherché un niveau au-dessus
du dépôt (``../checkup_complet.paths.json``), afin que les chemins propres au
poste local ne modifient jamais le manifeste ORI-C. Les valeurs ``null`` sont ignorées. Si une
partie d'un lot externe est renseignée, le lot doit être complet : un chemin
fourni mais absent est une erreur, jamais un simple avertissement.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
DEFAULT_CONFIG = ROOT.parent / "checkup_complet.paths.json"
EXPECTED_SOURCE_RESULT = (
    ROOT
    / "plan_directeur"
    / "campagne_centrale_2026_08_11"
    / "resultats"
    / "INSPECTION_SOURCES_RECUPEREES_2026_08_12.json"
)
PALMOD_ACQUISITION = (
    ROOT
    / "02_branche_systeme_solaire"
    / "paleo_history_01"
    / "PALEO_HISTORY_02_ACQUISITION.json"
)

EXTERNAL_KEYS = (
    "magnetic_u1506",
    "magnetic_u1537",
    "farough_pdf",
    "farough_original",
    "edc3_pdf",
    "palmod_zip",
    "palmod_ensemble",
)
SOURCE_BUNDLE_KEYS = (
    "magnetic_u1506",
    "magnetic_u1537",
    "farough_pdf",
    "farough_original",
    "edc3_pdf",
)


@dataclass
class Step:
    name: str
    command: list[str] | None
    status: str
    returncode: int | None
    seconds: float
    log: str | None = None
    detail: str | None = None


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_path(value: Any, config_path: Path, base_dir: Path | None) -> Path | None:
    if value is None or value == "":
        return None
    if not isinstance(value, str):
        raise ValueError(f"un chemin doit être une chaîne ou null, reçu {type(value).__name__}")
    expanded = os.path.expandvars(os.path.expanduser(value))
    path = Path(expanded)
    if not path.is_absolute():
        path = (base_dir or config_path.parent) / path
    return path.resolve()


def load_config(path: Path) -> dict[str, Path | None]:
    if not path.exists():
        raise FileNotFoundError(f"configuration absente : {path}")
    raw = load_json(path)
    if not isinstance(raw, dict):
        raise ValueError("la configuration doit être un objet JSON")
    unknown = sorted(set(raw) - set(EXTERNAL_KEYS) - {"base_dir"})
    if unknown:
        raise ValueError(f"clés inconnues dans la configuration : {', '.join(unknown)}")
    base_dir = resolve_path(raw.get("base_dir"), path, None) if raw.get("base_dir") else None
    return {key: resolve_path(raw.get(key), path, base_dir) for key in EXTERNAL_KEYS}


def terminate_process_tree(process: subprocess.Popen[Any]) -> None:
    if process.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        return
    try:
        os.killpg(process.pid, 15)
        process.wait(timeout=5)
    except Exception:
        try:
            os.killpg(process.pid, 9)
        except Exception:
            process.kill()


class Runner:
    def __init__(self, output_dir: Path, timeout: int, fail_fast: bool) -> None:
        self.output_dir = output_dir
        self.logs = output_dir / "logs"
        self.logs.mkdir(parents=True, exist_ok=True)
        self.timeout = timeout
        self.fail_fast = fail_fast
        self.steps: list[Step] = []
        self.counter = 0
        self.env = os.environ.copy()
        self.env["PYTHONUTF8"] = "1"
        self.env.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")
        self.env.setdefault("OPENBLAS_NUM_THREADS", "1")
        self.env.setdefault("OMP_NUM_THREADS", "1")
        self.env.setdefault("MPLCONFIGDIR", str(output_dir / "mplconfig"))

    def record(self, name: str, status: str, detail: str | None = None) -> Step:
        step = Step(name, None, status, None, 0.0, None, detail)
        self.steps.append(step)
        marker = {"PASS": "OK", "FAIL": "ECHEC", "SKIP": "SAUT", "WARN": "AVERT"}.get(status, status)
        print(f"[{marker}] {name}" + (f" — {detail}" if detail else ""), flush=True)
        if status == "FAIL" and self.fail_fast:
            raise RuntimeError(detail or name)
        return step

    def run(
        self,
        name: str,
        command: list[str],
        *,
        cwd: Path = ROOT,
        timeout: int | None = None,
        allow_failure: bool = False,
    ) -> Step:
        self.counter += 1
        safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in name.lower())[:80]
        log_path = self.logs / f"{self.counter:02d}_{safe}.log"
        started = time.monotonic()
        print(f"[RUN] {name}", flush=True)
        with log_path.open("wb") as log:
            process = subprocess.Popen(
                command,
                cwd=cwd,
                stdout=log,
                stderr=subprocess.STDOUT,
                env=self.env,
                start_new_session=True,
            )
            timed_out = False
            try:
                returncode = process.wait(timeout=timeout or self.timeout)
            except subprocess.TimeoutExpired:
                timed_out = True
                terminate_process_tree(process)
                returncode = 124
        elapsed = time.monotonic() - started
        status = "PASS" if returncode == 0 else ("WARN" if allow_failure else "FAIL")
        detail = f"code={returncode}, {elapsed:.1f}s"
        if timed_out:
            detail += ", délai dépassé"
        step = Step(name, command, status, returncode, elapsed, str(log_path), detail)
        self.steps.append(step)
        marker = "OK" if status == "PASS" else ("AVERT" if status == "WARN" else "ECHEC")
        print(f"[{marker}] {name} — {detail}", flush=True)
        if status == "FAIL":
            try:
                tail = log_path.read_text(encoding="utf-8", errors="replace").splitlines()[-18:]
                if tail:
                    print("\n".join("    " + line for line in tail), flush=True)
            except OSError:
                pass
            if self.fail_fast:
                raise RuntimeError(f"étape échouée : {name}")
        return step


def compare_semantic_json(actual: Path, expected: Path) -> tuple[bool, str]:
    if not expected.exists():
        return False, f"résultat versionné absent : {expected.relative_to(ROOT)}"
    left = load_json(actual)
    right = load_json(expected)
    if left == right:
        return True, "objet JSON sémantiquement identique au résultat versionné"

    differences: list[str] = []

    def walk(a: Any, b: Any, prefix: str = "$", limit: int = 12) -> None:
        if len(differences) >= limit:
            return
        if type(a) is not type(b):
            differences.append(f"{prefix}: type {type(a).__name__} != {type(b).__name__}")
            return
        if isinstance(a, dict):
            for key in sorted(set(a) | set(b)):
                if key not in a:
                    differences.append(f"{prefix}.{key}: absent du recalcul")
                elif key not in b:
                    differences.append(f"{prefix}.{key}: absent du versionné")
                else:
                    walk(a[key], b[key], f"{prefix}.{key}", limit)
                if len(differences) >= limit:
                    return
        elif isinstance(a, list):
            if len(a) != len(b):
                differences.append(f"{prefix}: longueur {len(a)} != {len(b)}")
                return
            for index, (x, y) in enumerate(zip(a, b)):
                walk(x, y, f"{prefix}[{index}]", limit)
                if len(differences) >= limit:
                    return
        elif a != b:
            differences.append(f"{prefix}: {a!r} != {b!r}")

    walk(left, right)
    return False, "; ".join(differences) or "objets JSON différents"


def validate_external_paths(config: dict[str, Path | None], runner: Runner) -> bool:
    ok = True
    for key, path in config.items():
        if path is not None and not path.exists():
            runner.record(f"chemin externe {key}", "FAIL", f"introuvable : {path}")
            ok = False
    supplied_bundle = [key for key in SOURCE_BUNDLE_KEYS if config[key] is not None]
    if supplied_bundle and len(supplied_bundle) != len(SOURCE_BUNDLE_KEYS):
        missing = [key for key in SOURCE_BUNDLE_KEYS if config[key] is None]
        runner.record(
            "lot externe U1506/U1537/Farough/EDC3",
            "FAIL",
            "configuration partielle, chemins null : " + ", ".join(missing),
        )
        ok = False
    return ok


def run_external_source_audit(config: dict[str, Path | None], runner: Runner) -> None:
    if not any(config[key] is not None for key in SOURCE_BUNDLE_KEYS):
        runner.record("réinspection U1506/U1537/Farough/EDC3", "SKIP", "aucun chemin fourni")
        return
    if not all(config[key] is not None and config[key].exists() for key in SOURCE_BUNDLE_KEYS):
        return
    output = runner.output_dir / "INSPECTION_SOURCES_RECUPEREES_recalculee.json"
    command = [
        sys.executable,
        "plan_directeur/campagne_centrale_2026_08_11/analyser_sources_recuperees.py",
        "--magnetic-u1506", str(config["magnetic_u1506"]),
        "--magnetic-u1537", str(config["magnetic_u1537"]),
        "--edc3", str(config["edc3_pdf"]),
        "--farough-pdf", str(config["farough_pdf"]),
        "--farough-original", str(config["farough_original"]),
        "--output", str(output),
    ]
    step = runner.run("réinspection U1506/U1537/Farough/EDC3", command, timeout=max(runner.timeout, 900))
    if step.status != "PASS":
        return
    same, detail = compare_semantic_json(output, EXPECTED_SOURCE_RESULT)
    runner.record("comparaison sémantique des sources récupérées", "PASS" if same else "FAIL", detail)


def run_palmod_audit(config: dict[str, Path | None], runner: Runner) -> None:
    archive = config["palmod_zip"]
    ensemble = config["palmod_ensemble"]
    if archive is None:
        if ensemble is not None:
            runner.record("PALMOD", "FAIL", "palmod_ensemble fourni sans palmod_zip")
        else:
            runner.record("PALMOD", "SKIP", "aucun chemin fourni")
        return
    if not archive.exists() or (ensemble is not None and not ensemble.exists()):
        return
    catalog = runner.output_dir / "palmod_ensemble_urls.json"
    command = [
        sys.executable,
        "02_branche_systeme_solaire/paleo_history_01/verifier_palmod_v2.py",
        str(archive),
        "--write-catalog", str(catalog),
    ]
    if ensemble is not None:
        command += ["--ensemble", str(ensemble)]
    step = runner.run("vérification PALMOD", command, timeout=max(runner.timeout, 900))
    if step.status != "PASS":
        return
    expected = load_json(PALMOD_ACQUISITION)["compilation"]["sha256"]
    actual = sha256(archive)
    runner.record(
        "empreinte PALMOD",
        "PASS" if actual == expected else "FAIL",
        f"sha256={actual}" + ("" if actual == expected else f", attendu={expected}"),
    )


def run_state_suites(runner: Runner) -> None:
    names = [
        "priorites",
        "calibrage",
        "recherche-suivante",
        "socle",
        "memoire",
        "astronomie",
        "spin-orbite",
        "formalismes-externes",
        "trois-branches",
    ]
    for name in names:
        step = runner.run(
            f"suite globale {name}",
            [sys.executable, "etat_des_tests.py", "--suite", name],
            timeout=max(runner.timeout, 900),
        )
        if step.status != "PASS" or not step.log:
            continue
        try:
            payload = json.loads(Path(step.log).read_text(encoding="utf-8", errors="replace").strip())
        except (OSError, json.JSONDecodeError) as exc:
            runner.record(f"verdict suite globale {name}", "FAIL", f"sortie JSON illisible : {exc}")
            continue
        if payload.get("disponible") is False:
            runner.record(
                f"verdict suite globale {name}",
                "FAIL",
                f"suite non exécutable : {payload.get('motif', 'motif non fourni')}",
            )
            continue
        internal_code = int(payload.get("code_retour", 0) or 0)
        failed = int(payload.get("echoues", 0) or 0)
        status = "PASS" if internal_code == 0 and failed == 0 else "FAIL"
        detail = (
            f"réussis={payload.get('reussis', payload.get('total', '?'))}, "
            f"échoués={failed}, code_interne={internal_code}"
        )
        runner.record(f"verdict suite globale {name}", status, detail)


def write_report(runner: Runner, config_path: Path, config: dict[str, Path | None]) -> tuple[Path, Path]:
    finished = datetime.now().astimezone()
    failed = [step for step in runner.steps if step.status == "FAIL"]
    warnings = [step for step in runner.steps if step.status == "WARN"]
    skipped = [step for step in runner.steps if step.status == "SKIP"]
    payload = {
        "schema": "oric.checkup-complet.v1",
        "finished_at": finished.isoformat(),
        "repository": str(ROOT),
        "config": str(config_path),
        "external_paths": {key: str(value) if value else None for key, value in config.items()},
        "summary": {
            "steps": len(runner.steps),
            "passed": sum(step.status == "PASS" for step in runner.steps),
            "failed": len(failed),
            "warnings": len(warnings),
            "skipped": len(skipped),
            "verdict": "PASS" if not failed else "FAIL",
        },
        "steps": [asdict(step) for step in runner.steps],
    }
    json_path = runner.output_dir / "RAPPORT_CHECKUP_COMPLET.json"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

    lines = [
        "# Rapport check-up complet ORI-C",
        "",
        f"- Verdict : **{payload['summary']['verdict']}**",
        f"- Étapes : {payload['summary']['steps']}",
        f"- Réussies : {payload['summary']['passed']}",
        f"- Échecs : {payload['summary']['failed']}",
        f"- Avertissements : {payload['summary']['warnings']}",
        f"- Sauts : {payload['summary']['skipped']}",
        f"- Terminé : {finished.isoformat()}",
        "",
        "## Étapes",
        "",
        "| Statut | Étape | Durée | Détail |",
        "|---|---|---:|---|",
    ]
    for step in runner.steps:
        detail = (step.detail or "").replace("|", "\\|")
        lines.append(f"| {step.status} | {step.name} | {step.seconds:.1f}s | {detail} |")
    md_path = runner.output_dir / "RAPPORT_CHECKUP_COMPLET.md"
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return json_path, md_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, help="dossier de rapport hors du dépôt")
    parser.add_argument("--timeout", type=int, default=600, help="délai par étape en secondes")
    parser.add_argument("--fail-fast", action="store_true", help="arrête au premier échec")
    parser.add_argument("--quick", action="store_true", help="saute les neuf suites globales longues")
    parser.add_argument("--dry-run", action="store_true", help="valide la configuration sans exécuter les calculs")
    args = parser.parse_args(argv)

    config_path = args.config.expanduser().resolve()
    try:
        config = load_config(config_path)
    except Exception as exc:
        print(f"Configuration invalide : {exc}", file=sys.stderr)
        return 2

    if args.output_dir:
        output_dir = args.output_dir.expanduser().resolve()
    else:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(tempfile.gettempdir()) / "oric_checkup_complet" / stamp
    output_dir.mkdir(parents=True, exist_ok=True)
    runner = Runner(output_dir, max(args.timeout, 30), args.fail_fast)

    required = [
        ROOT / "build_manifest.py",
        ROOT / "verifier_dossier.py",
        ROOT / "scripts" / "valider_tout.py",
        ROOT / "etat_des_tests.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        runner.record("préflight dépôt", "FAIL", "fichiers absents : " + ", ".join(missing))
    else:
        runner.record("préflight dépôt", "PASS", f"racine={ROOT}")
    validate_external_paths(config, runner)

    if args.dry_run:
        runner.record("dry-run", "PASS", "configuration et chemins contrôlés, aucun calcul lancé")
        json_report, md_report = write_report(runner, config_path, config)
        print(f"Rapport JSON : {json_report}")
        print(f"Rapport Markdown : {md_report}")
        return 1 if any(step.status == "FAIL" for step in runner.steps) else 0

    runner.run("manifeste initial", [sys.executable, "build_manifest.py", "verify"])
    runner.run("validation rapide stricte", [sys.executable, "scripts/valider_tout.py", "--strict-lfs"], timeout=max(args.timeout, 900))

    run_external_source_audit(config, runner)
    run_palmod_audit(config, runner)

    runner.run(
        "normalisation paléoclimatique",
        [sys.executable, "02_branche_systeme_solaire/paleo_history_01/normaliser_donnees.py"],
    )
    runner.run(
        "tests paléoclimat/PALMOD",
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
         "02_branche_systeme_solaire/paleo_history_01/tests"],
    )

    runner.run(
        "généalogie cosmique — recalcul complet",
        [sys.executable, "01_branche_matiere/genealogie_cosmique_quantitative/run_all.py"],
        timeout=max(args.timeout, 1200),
    )
    gcq_test_command = [
        sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
    ]
    if args.quick:
        gcq_test_command += [
            "01_branche_matiere/genealogie_cosmique_quantitative/tests/test_distribution_26al.py",
            "01_branche_matiere/genealogie_cosmique_quantitative/tests/test_information_interetages.py::test_normalized_mutual_information_bounds",
        ]
    else:
        gcq_test_command += ["01_branche_matiere/genealogie_cosmique_quantitative/tests"]
    runner.run(
        "généalogie cosmique — tests" + (" rapides" if args.quick else ""),
        gcq_test_command,
        timeout=max(args.timeout, 1800),
    )

    runner.run(
        "campagne centrale — recalcul",
        [sys.executable, "plan_directeur/campagne_centrale_2026_08_11/run_all.py"],
    )
    runner.run(
        "campagne centrale — tests",
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
         "plan_directeur/campagne_centrale_2026_08_11/tests"],
    )

    if args.quick:
        runner.record(
            "campagne maximale trois branches — recalcul et tests",
            "SKIP",
            "mode --quick",
        )
    else:
        runner.run(
            "campagne maximale trois branches — recalcul",
            [sys.executable, "plan_directeur/campagne_maximale_trois_branches/run_all.py"],
            timeout=max(args.timeout, 1800),
        )
        runner.run(
            "campagne maximale trois branches — tests",
            [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
             "plan_directeur/campagne_maximale_trois_branches/tests"],
            timeout=max(args.timeout, 900),
        )

    runner.run("audit transversal", [sys.executable, "plan_directeur/audit_transversal.py"])

    if args.quick:
        runner.record("neuf suites globales", "SKIP", "mode --quick")
    else:
        run_state_suites(runner)

    runner.run("reconstruction registre de preuves", [sys.executable, "scripts/construire_registre_preuves.py"])
    runner.run("validation registre de preuves", [sys.executable, "scripts/valider_registre_preuves.py"])
    runner.run("validation finale stricte", [sys.executable, "scripts/valider_tout.py", "--strict-lfs"], timeout=max(args.timeout, 900))
    runner.run("manifeste final", [sys.executable, "build_manifest.py", "verify"])

    if shutil.which("git") and (ROOT / ".git").exists():
        runner.run("état Git final", ["git", "status", "--short"], allow_failure=True)
    else:
        runner.record("état Git final", "SKIP", "Git ou .git absent")

    json_report, md_report = write_report(runner, config_path, config)
    failures = [step for step in runner.steps if step.status == "FAIL"]
    print(f"\nRapport JSON : {json_report}")
    print(f"Rapport Markdown : {md_report}")
    print(f"Verdict : {'ECHEC' if failures else 'OK'}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
