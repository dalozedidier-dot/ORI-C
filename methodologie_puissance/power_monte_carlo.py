#!/usr/bin/env python3
"""Cadre reproductible de puissance a priori pour les pipelines ORI-C.

Le moteur ne simule jamais des scores de folds comme s'ils étaient des
observations indépendantes. Un adaptateur propre au protocole doit simuler les
observations ou trajectoires, réexécuter le pipeline complet et retourner les
critères de décision préenregistrés.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from statistics import NormalDist
from types import ModuleType
from typing import Any, Mapping, Sequence

import numpy as np

VERSION = "1.0"
FORBIDDEN_INDEPENDENT_UNITS = {
    "fold",
    "folds",
    "cv_fold",
    "cv_folds",
    "cross_validation_fold",
    "cross_validation_folds",
}
EFFECT_TYPES = {
    "absolute_difference",
    "relative_improvement",
    "standardized_difference",
    "ratio_to_numerical_noise",
}


class PlanError(ValueError):
    """Plan de puissance absent, ambigu ou incohérent."""


@dataclass(frozen=True)
class Adapter:
    path: Path
    module: ModuleType
    sha256: str


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_plan(path: Path) -> dict[str, Any]:
    try:
        plan = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PlanError(f"plan illisible: {path}: {exc}") from exc
    validate_plan(plan)
    return plan


def _number(value: Any, name: str, *, lower: float | None = None, upper: float | None = None) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise PlanError(f"{name} doit être un nombre fini")
    number = float(value)
    if lower is not None and number <= lower:
        raise PlanError(f"{name} doit être supérieur à {lower}")
    if upper is not None and number >= upper:
        raise PlanError(f"{name} doit être inférieur à {upper}")
    return number


def _positive_integer(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise PlanError(f"{name} doit être un entier strictement positif")
    return value


def validate_plan(plan: Mapping[str, Any]) -> None:
    required = {
        "protocol_id",
        "analysis_frozen_before_data",
        "independent_unit",
        "primary_metric",
        "effect",
        "alpha",
        "target_power",
        "noise_estimation",
        "test_definition",
        "controls",
        "success_rule",
        "simulation_model",
        "adapter",
        "preliminary_simulations",
        "confirmation_simulations",
        "seed",
    }
    missing = sorted(required - set(plan))
    if missing:
        raise PlanError(f"champs manquants: {', '.join(missing)}")

    for name in ("protocol_id", "primary_metric", "test_definition", "simulation_model"):
        if not isinstance(plan[name], str) or not plan[name].strip():
            raise PlanError(f"{name} doit être une chaîne non vide")

    if plan["analysis_frozen_before_data"] is not True:
        raise PlanError("analysis_frozen_before_data doit être true avant l'acquisition")

    unit = plan["independent_unit"]
    if not isinstance(unit, str) or not unit.strip():
        raise PlanError("independent_unit doit être une chaîne non vide")
    normalized_unit = unit.strip().lower().replace("-", "_").replace(" ", "_")
    if normalized_unit in FORBIDDEN_INDEPENDENT_UNITS or "fold" in normalized_unit:
        raise PlanError("un fold de validation croisée n'est pas une unité indépendante")

    _number(plan["alpha"], "alpha", lower=0.0, upper=1.0)
    _number(plan["target_power"], "target_power", lower=0.0, upper=1.0)

    effect = plan["effect"]
    if not isinstance(effect, Mapping):
        raise PlanError("effect doit être un objet")
    if effect.get("type") not in EFFECT_TYPES:
        raise PlanError(f"effect.type doit appartenir à {sorted(EFFECT_TYPES)}")
    _number(effect.get("sesoi"), "effect.sesoi", lower=0.0)
    if not isinstance(effect.get("justification"), str) or not effect["justification"].strip():
        raise PlanError("effect.justification doit expliquer la signification scientifique du SESOI")
    if effect["type"] == "relative_improvement":
        _number(effect.get("baseline"), "effect.baseline", lower=0.0)
    if effect["type"] == "standardized_difference":
        _number(effect.get("scale"), "effect.scale", lower=0.0)

    noise = plan["noise_estimation"]
    if not isinstance(noise, Mapping):
        raise PlanError("noise_estimation doit être un objet")
    for name in ("source", "description"):
        if not isinstance(noise.get(name), str) or not noise[name].strip():
            raise PlanError(f"noise_estimation.{name} doit être renseigné")
    if "value" in noise:
        _number(noise["value"], "noise_estimation.value", lower=0.0)
    if effect["type"] == "ratio_to_numerical_noise" and "value" not in noise:
        raise PlanError("ratio_to_numerical_noise exige noise_estimation.value")

    for name in ("controls", "success_rule"):
        values = plan[name]
        if not isinstance(values, list) or not values or not all(isinstance(item, str) and item.strip() for item in values):
            raise PlanError(f"{name} doit être une liste non vide de chaînes")
        if len(set(values)) != len(values):
            raise PlanError(f"{name} contient des doublons")

    adapter = plan["adapter"]
    if not isinstance(adapter, Mapping) or not isinstance(adapter.get("path"), str) or not adapter["path"].strip():
        raise PlanError("adapter.path doit désigner l'adaptateur du pipeline réel")
    function = adapter.get("function", "simulate_and_evaluate")
    if not isinstance(function, str) or not function.strip():
        raise PlanError("adapter.function doit être une chaîne non vide")

    preliminary = _positive_integer(plan["preliminary_simulations"], "preliminary_simulations")
    confirmation = _positive_integer(plan["confirmation_simulations"], "confirmation_simulations")
    if preliminary < 500:
        raise PlanError("preliminary_simulations doit être au moins 500")
    if confirmation < 10_000:
        raise PlanError("confirmation_simulations doit être au moins 10000 près du seuil")
    if isinstance(plan["seed"], bool) or not isinstance(plan["seed"], int) or plan["seed"] < 0:
        raise PlanError("seed doit être un entier positif ou nul")

    if "available_n" in plan:
        _positive_integer(plan["available_n"], "available_n")
    if "sample_size_grid" in plan:
        grid = plan["sample_size_grid"]
        if not isinstance(grid, list) or not grid:
            raise PlanError("sample_size_grid doit être une liste non vide")
        sizes = [_positive_integer(value, "sample_size_grid[]") for value in grid]
        if sizes != sorted(set(sizes)):
            raise PlanError("sample_size_grid doit être strictement croissante et sans doublon")
    if "effect_grid" in plan:
        grid = plan["effect_grid"]
        if not isinstance(grid, list) or not grid:
            raise PlanError("effect_grid doit être une liste non vide")
        effects = [_number(value, "effect_grid[]", lower=0.0) for value in grid]
        if effects != sorted(set(effects)):
            raise PlanError("effect_grid doit être strictement croissante et sans doublon")


def effect_context(plan: Mapping[str, Any], sesoi: float | None = None) -> dict[str, float | str]:
    effect = plan["effect"]
    value = float(effect["sesoi"] if sesoi is None else sesoi)
    if value <= 0:
        raise PlanError("la taille d'effet doit être strictement positive")
    effect_type = effect["type"]
    if effect_type == "absolute_difference":
        absolute = value
    elif effect_type == "relative_improvement":
        absolute = float(effect["baseline"]) * value
    elif effect_type == "standardized_difference":
        absolute = float(effect["scale"]) * value
    else:
        absolute = float(plan["noise_estimation"]["value"]) * value
    return {"type": effect_type, "value": value, "absolute": absolute}


def wilson_interval(successes: int, trials: int, confidence: float = 0.95) -> tuple[float, float]:
    if trials <= 0 or successes < 0 or successes > trials:
        raise ValueError("comptage binomial invalide")
    if not 0.0 < confidence < 1.0:
        raise ValueError("confidence doit être comprise entre 0 et 1")
    z = NormalDist().inv_cdf(0.5 + confidence / 2.0)
    p = successes / trials
    denominator = 1.0 + z * z / trials
    center = (p + z * z / (2.0 * trials)) / denominator
    margin = z * math.sqrt((p * (1.0 - p) + z * z / (4.0 * trials)) / trials) / denominator
    return max(0.0, center - margin), min(1.0, center + margin)


def load_adapter(plan: Mapping[str, Any], repo_root: Path) -> Adapter:
    path = (repo_root / plan["adapter"]["path"]).resolve()
    if not path.is_file():
        raise PlanError(f"adaptateur absent: {path}")
    module_name = f"oric_power_adapter_{sha256_file(path)[:16]}"
    specification = importlib.util.spec_from_file_location(module_name, path)
    if specification is None or specification.loader is None:
        raise PlanError(f"adaptateur impossible à charger: {path}")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    function_name = plan["adapter"].get("function", "simulate_and_evaluate")
    if not callable(getattr(module, function_name, None)):
        raise PlanError(f"fonction absente dans l'adaptateur: {function_name}")
    return Adapter(path=path, module=module, sha256=sha256_file(path))


def _run_once(adapter: Adapter, plan: Mapping[str, Any], rng: np.random.Generator, n: int, effect: Mapping[str, Any]) -> dict[str, Any]:
    function_name = plan["adapter"].get("function", "simulate_and_evaluate")
    result = getattr(adapter.module, function_name)(rng=rng, plan=plan, n=n, effect=effect)
    if not isinstance(result, Mapping):
        raise PlanError("l'adaptateur doit retourner un objet de critères")
    missing = [name for name in plan["success_rule"] if name not in result]
    if missing:
        raise PlanError(f"critères absents du résultat de l'adaptateur: {', '.join(missing)}")
    for name in plan["success_rule"]:
        if not isinstance(result[name], (bool, np.bool_)):
            raise PlanError(f"le critère {name} doit être booléen")
    return dict(result)


def estimate_power(
    plan: Mapping[str, Any],
    adapter: Adapter,
    *,
    n: int,
    sesoi: float | None = None,
    simulations: int | None = None,
    seed: int | None = None,
) -> dict[str, Any]:
    validate_plan(plan)
    n = _positive_integer(n, "n")
    simulations = _positive_integer(
        int(plan["confirmation_simulations"] if simulations is None else simulations),
        "simulations",
    )
    seed_value = int(plan["seed"] if seed is None else seed)
    effect = effect_context(plan, sesoi)
    criterion_counts = {name: 0 for name in plan["success_rule"]}
    joint_successes = 0
    child_seeds = np.random.SeedSequence(seed_value).spawn(simulations)

    for child_seed in child_seeds:
        result = _run_once(adapter, plan, np.random.default_rng(child_seed), n, effect)
        for name in criterion_counts:
            criterion_counts[name] += int(bool(result[name]))
        joint_successes += int(all(bool(result[name]) for name in plan["success_rule"]))

    lower, upper = wilson_interval(joint_successes, simulations)
    return {
        "engine_version": VERSION,
        "protocol_id": plan["protocol_id"],
        "independent_unit": plan["independent_unit"],
        "n_independent_units": n,
        "effect": effect,
        "alpha": float(plan["alpha"]),
        "target_power": float(plan["target_power"]),
        "simulations": simulations,
        "seed": seed_value,
        "joint_success_rule": list(plan["success_rule"]),
        "joint_successes": joint_successes,
        "power": joint_successes / simulations,
        "wilson_95": {"lower": lower, "upper": upper},
        "criterion_rates": {
            name: criterion_counts[name] / simulations for name in plan["success_rule"]
        },
        "adapter": {
            "path": plan["adapter"]["path"],
            "sha256": adapter.sha256,
        },
    }


def scan_required_n(plan: Mapping[str, Any], adapter: Adapter, sizes: Sequence[int] | None = None) -> dict[str, Any]:
    validate_plan(plan)
    selected_sizes = list(plan.get("sample_size_grid", []) if sizes is None else sizes)
    if not selected_sizes:
        raise PlanError("sample_size_grid est requis pour rechercher n")
    selected_sizes = [_positive_integer(int(value), "n") for value in selected_sizes]
    if selected_sizes != sorted(set(selected_sizes)):
        raise PlanError("les tailles doivent être strictement croissantes")

    preliminary = [
        estimate_power(
            plan,
            adapter,
            n=n,
            simulations=int(plan["preliminary_simulations"]),
            seed=int(plan["seed"]) + n,
        )
        for n in selected_sizes
    ]
    target = float(plan["target_power"])
    candidates = [row["n_independent_units"] for row in preliminary if row["wilson_95"]["upper"] >= target]
    if not candidates:
        candidates = [selected_sizes[-1]]

    confirmation = []
    required_n = None
    for n in candidates:
        row = estimate_power(
            plan,
            adapter,
            n=n,
            simulations=int(plan["confirmation_simulations"]),
            seed=int(plan["seed"]) + 1_000_000 + n,
        )
        confirmation.append(row)
        if row["wilson_95"]["lower"] >= target:
            required_n = n
            break

    return {
        "engine_version": VERSION,
        "protocol_id": plan["protocol_id"],
        "selection_rule": "plus petit n dont la borne inférieure de Wilson atteint la puissance cible",
        "target_power": target,
        "required_n": required_n,
        "preliminary": preliminary,
        "confirmation": confirmation,
    }


def minimum_detectable_effect(plan: Mapping[str, Any], adapter: Adapter, effects: Sequence[float] | None = None, n: int | None = None) -> dict[str, Any]:
    validate_plan(plan)
    selected_effects = list(plan.get("effect_grid", []) if effects is None else effects)
    if not selected_effects:
        raise PlanError("effect_grid est requis pour rechercher l'effet minimal détectable")
    selected_effects = [float(value) for value in selected_effects]
    if any(value <= 0 or not math.isfinite(value) for value in selected_effects):
        raise PlanError("effect_grid doit contenir des nombres strictement positifs")
    if selected_effects != sorted(set(selected_effects)):
        raise PlanError("effect_grid doit être strictement croissante")
    sample_size_value = plan.get("available_n") if n is None else n
    if sample_size_value is None:
        raise PlanError("available_n ou --n est requis pour rechercher l’effet minimal détectable")
    sample_size = int(sample_size_value)
    _positive_integer(sample_size, "available_n")

    target = float(plan["target_power"])
    rows = []
    detectable = None
    for index, value in enumerate(selected_effects):
        row = estimate_power(
            plan,
            adapter,
            n=sample_size,
            sesoi=value,
            simulations=int(plan["confirmation_simulations"]),
            seed=int(plan["seed"]) + 2_000_000 + index,
        )
        rows.append(row)
        if row["wilson_95"]["lower"] >= target:
            detectable = value
            break
    return {
        "engine_version": VERSION,
        "protocol_id": plan["protocol_id"],
        "selection_rule": "plus petit effet dont la borne inférieure de Wilson atteint la puissance cible",
        "target_power": target,
        "n_independent_units": sample_size,
        "minimum_detectable_effect": detectable,
        "evaluations": rows,
    }


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    temporary.replace(path)


def find_power_plans(root: Path) -> list[Path]:
    return sorted(
        path for path in root.rglob("*.json")
        if path.name == "POWER_PLAN.json" or path.name.endswith("_POWER_PLAN.json")
    )


def command_validate_all(root: Path) -> int:
    plans = find_power_plans(root)
    errors = []
    for path in plans:
        try:
            read_plan(path)
        except PlanError as exc:
            errors.append(f"{path.relative_to(root)}: {exc}")
    payload = {"plans": len(plans), "errors": errors, "status": "ok" if not errors else "error"}
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 1 if errors else 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="valider un plan")
    validate_parser.add_argument("plan", type=Path)

    validate_all_parser = subparsers.add_parser("validate-all", help="valider tous les POWER_PLAN.json")
    validate_all_parser.add_argument("root", type=Path, nargs="?", default=Path("."))

    for command in ("estimate", "scan-n", "mde"):
        child = subparsers.add_parser(command)
        child.add_argument("plan", type=Path)
        child.add_argument("--repo-root", type=Path, default=Path("."))
        child.add_argument("--output", type=Path, required=True)
        if command == "estimate":
            child.add_argument("--n", type=int)
            child.add_argument("--simulations", type=int)
            child.add_argument("--effect", type=float)
        elif command == "mde":
            child.add_argument("--n", type=int)

    args = parser.parse_args(argv)
    if args.command == "validate-all":
        return command_validate_all(args.root.resolve())

    try:
        plan = read_plan(args.plan)
        if args.command == "validate":
            print(json.dumps({"plan": str(args.plan), "status": "ok"}, ensure_ascii=False, indent=2))
            return 0
        adapter = load_adapter(plan, args.repo_root.resolve())
        if args.command == "estimate":
            n = args.n if args.n is not None else plan.get("available_n")
            if n is None:
                raise PlanError("--n ou available_n est requis")
            payload = estimate_power(
                plan,
                adapter,
                n=int(n),
                sesoi=args.effect,
                simulations=args.simulations,
            )
        elif args.command == "scan-n":
            payload = scan_required_n(plan, adapter)
        else:
            payload = minimum_detectable_effect(plan, adapter, n=args.n)
        payload["plan"] = {
            "path": str(args.plan),
            "sha256": sha256_file(args.plan),
        }
        write_json(args.output, payload)
        print(json.dumps({"output": str(args.output), "status": "ok"}, ensure_ascii=False, indent=2))
        return 0
    except PlanError as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
