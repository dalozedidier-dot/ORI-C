from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any
import json


class ExecutionMode(StrEnum):
    AUTOMATED = "automated"
    DATA_REQUIRED = "data_required"
    EXTERNAL_CODE = "external_code"
    LABORATORY = "laboratory"
    HUMAN_REVIEW = "human_review"
    EXTERNAL_REPLICATION = "external_replication"


class Outcome(StrEnum):
    """Résultat technique de l'exécution du pipeline."""

    PASS = "pass"
    FAIL = "fail"
    SKIP = "skip"
    BLOCKED = "blocked"
    ERROR = "error"
    NOT_RUN = "not_run"


class ScientificVerdict(StrEnum):
    """Verdict scientifique séparé du statut technique.

    Une exécution informatique réussie ne devient un verdict scientifique que si un
    critère préenregistré et gelé est disponible.
    """

    UNDETERMINED = "undetermined"
    SUPPORTS = "supports"
    DOES_NOT_SUPPORT = "does_not_support"
    INCONCLUSIVE = "inconclusive"
    NOT_APPLICABLE = "not_applicable"


@dataclass(frozen=True)
class TestSpec:
    # Pytest otherwise tries to collect this imported domain model as a test class.
    __test__ = False

    test_id: str
    wp: str
    section: str
    ordinal: int
    description: str
    mode: ExecutionMode
    engine: str
    required_datasets: tuple[str, ...] = ()
    confirmatory: bool = False
    priority: int = 2
    source_line: int | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["mode"] = self.mode.value
        return data


@dataclass
class TestResult:
    test_id: str
    wp: str
    outcome: Outcome
    metric: float | None = None
    threshold: float | None = None
    message: str = ""
    details: dict[str, Any] = field(default_factory=dict)
    artifacts: list[str] = field(default_factory=list)
    duration_s: float = 0.0
    scientific_verdict: ScientificVerdict = ScientificVerdict.UNDETERMINED
    criterion_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["outcome"] = self.outcome.value
        data["scientific_verdict"] = self.scientific_verdict.value
        return data


@dataclass
class CampaignResult:
    run_id: str
    started_at: str
    finished_at: str
    root: str
    results: list[TestResult]
    environment: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def counts(self) -> dict[str, int]:
        counts = {item.value: 0 for item in Outcome}
        for result in self.results:
            counts[result.outcome.value] += 1
        return counts

    @property
    def scientific_counts(self) -> dict[str, int]:
        counts = {item.value: 0 for item in ScientificVerdict}
        for result in self.results:
            counts[result.scientific_verdict.value] += 1
        return counts

    def save(self, output_dir: Path) -> None:
        output_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "run_id": self.run_id,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "root": self.root,
            "counts": self.counts,
            "scientific_counts": self.scientific_counts,
            "environment": self.environment,
            "metadata": self.metadata,
            "results": [result.to_dict() for result in self.results],
        }
        (output_dir / "results.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
