from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any
import math

import pandas as pd

from .models import ScientificVerdict, TestSpec


OPERATORS = {">", ">=", "<", "<=", "==", "!=", "between", "finite", "nonzero"}


@dataclass(frozen=True)
class Criterion:
    criterion_id: str
    test_id: str
    metric_key: str
    operator: str
    threshold_low: float | None = None
    threshold_high: float | None = None
    frozen: bool = False
    confirmatory: bool = False
    expected_direction: str = ""
    notes: str = ""

    def __post_init__(self) -> None:
        if self.operator not in OPERATORS:
            raise ValueError(f"Opérateur de critère inconnu: {self.operator}")


class CriteriaRegistry:
    def __init__(self, criteria: list[Criterion]):
        self._criteria = {item.test_id: item for item in criteria}

    @classmethod
    def load(cls, path: Path | None) -> "CriteriaRegistry":
        if path is None or not Path(path).exists():
            return cls([])
        frame = pd.read_csv(path)
        records: list[Criterion] = []
        for row in frame.to_dict(orient="records"):
            metric_key = _text_or_empty(row.get("metric_key"))
            if not metric_key:
                continue
            records.append(
                Criterion(
                    criterion_id=_text_or_empty(row.get("criterion_id")) or f"CRIT-{row['test_id']}",
                    test_id=str(row["test_id"]),
                    metric_key=metric_key,
                    operator=str(row.get("operator") or "finite"),
                    threshold_low=_number_or_none(row.get("threshold_low")),
                    threshold_high=_number_or_none(row.get("threshold_high")),
                    frozen=_bool(row.get("frozen", False)),
                    confirmatory=_bool(row.get("confirmatory", False)),
                    expected_direction=_text_or_empty(row.get("expected_direction")),
                    notes=_text_or_empty(row.get("notes")),
                )
            )
        return cls(records)

    def get(self, test_id: str) -> Criterion | None:
        return self._criteria.get(test_id)


def _text_or_empty(value: Any) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return ""
    text = str(value).strip()
    return "" if text.casefold() == "nan" else text


def _number_or_none(value: Any) -> float | None:
    if value is None or (isinstance(value, float) and math.isnan(value)) or str(value).strip() == "":
        return None
    return float(value)


def _bool(value: Any) -> bool:
    return str(value).strip().casefold() in {"1", "true", "yes", "oui", "y"}


def nested_metric(details: dict[str, Any], key: str, fallback: float | None = None) -> float | None:
    if key in {"metric", "primary_metric"}:
        return fallback
    current: Any = details
    for part in key.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    try:
        return float(current)
    except (TypeError, ValueError):
        return None


def evaluate_criterion(
    criterion: Criterion | None,
    details: dict[str, Any],
    primary_metric: float | None,
) -> tuple[ScientificVerdict, float | None, str | None]:
    if criterion is None or not criterion.frozen:
        return ScientificVerdict.UNDETERMINED, None, None
    value = nested_metric(details, criterion.metric_key, fallback=primary_metric)
    if value is None or not math.isfinite(value):
        if criterion.operator == "finite":
            return ScientificVerdict.DOES_NOT_SUPPORT, value, criterion.criterion_id
        return ScientificVerdict.INCONCLUSIVE, value, criterion.criterion_id

    lo, hi = criterion.threshold_low, criterion.threshold_high
    op = criterion.operator
    # Correctif 1. Une borne supérieure se déclare naturellement dans
    # `threshold_high`, mais `<` et `<=` ne lisaient que `threshold_low` : le
    # critère échouait alors quelle que soit la valeur mesurée. Les opérateurs
    # d'inégalité acceptent désormais la borne du côté où elle est écrite.
    if op in {"<", "<=", ">", ">="} and lo is None and hi is not None:
        lo = hi
    if op == "finite":
        passed = math.isfinite(value)
    elif op == "nonzero":
        passed = value != 0.0
    elif op == ">":
        passed = lo is not None and value > lo
    elif op == ">=":
        passed = lo is not None and value >= lo
    elif op == "<":
        passed = lo is not None and value < lo
    elif op == "<=":
        passed = lo is not None and value <= lo
    elif op == "==":
        passed = lo is not None and math.isclose(value, lo, rel_tol=1e-12, abs_tol=1e-12)
    elif op == "!=":
        passed = lo is not None and not math.isclose(value, lo, rel_tol=1e-12, abs_tol=1e-12)
    elif op == "between":
        passed = lo is not None and hi is not None and lo <= value <= hi
    else:  # pragma: no cover - guarded by dataclass
        return ScientificVerdict.INCONCLUSIVE, value, criterion.criterion_id
    return (
        ScientificVerdict.SUPPORTS if passed else ScientificVerdict.DOES_NOT_SUPPORT,
        value,
        criterion.criterion_id,
    )


def write_criteria_template(specs: list[TestSpec], path: Path) -> Path:
    rows = []
    for spec in specs:
        rows.append(
            {
                "criterion_id": f"CRIT-{spec.test_id}",
                "test_id": spec.test_id,
                "wp": spec.wp,
                "description": spec.description,
                "metric_key": "",
                "operator": "finite",
                "threshold_low": "",
                "threshold_high": "",
                "frozen": False,
                "confirmatory": spec.confirmatory,
                "expected_direction": "",
                "notes": "À remplir et geler avant l'analyse confirmatoire.",
            }
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(path, index=False)
    return path
