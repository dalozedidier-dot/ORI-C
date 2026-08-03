from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import json

from .data_registry import SCHEMAS
from .engines import SUPPORTED_ENGINES
from .registry import Registry


@dataclass(frozen=True)
class AuditIssue:
    level: str
    code: str
    message: str


@dataclass(frozen=True)
class AuditReport:
    ok: bool
    catalogue_entries: int
    work_packages: int
    engines: int
    datasets: int
    issues: tuple[AuditIssue, ...]

    def to_dict(self) -> dict:
        data = asdict(self)
        data["issues"] = [asdict(issue) for issue in self.issues]
        return data


def audit_platform(root: Path, catalog: Path | None = None) -> AuditReport:
    root = Path(root)
    registry = Registry.load(catalog)
    specs = registry.all()
    issues: list[AuditIssue] = []

    unknown_engines = sorted({spec.engine for spec in specs} - SUPPORTED_ENGINES)
    for engine in unknown_engines:
        issues.append(AuditIssue("error", "UNKNOWN_ENGINE", engine))

    unknown_datasets = sorted(
        {dataset for spec in specs for dataset in spec.required_datasets} - set(SCHEMAS)
    )
    for dataset in unknown_datasets:
        issues.append(AuditIssue("error", "UNKNOWN_DATASET", dataset))

    plan = root / "docs" / "PLAN_DIRECTEUR_TESTS_ORI-C_COMPLET.md"
    if not plan.exists():
        issues.append(AuditIssue("error", "MISSING_PLAN", str(plan)))
    else:
        line_count = len(plan.read_text(encoding="utf-8").splitlines())
        invalid_lines = [spec.test_id for spec in specs if spec.source_line and spec.source_line > line_count]
        if invalid_lines:
            issues.append(
                AuditIssue(
                    "error",
                    "INVALID_SOURCE_LINES",
                    f"{len(invalid_lines)} identifiants hors du plan: {invalid_lines[:10]}",
                )
            )

    required = [
        root / "README.md",
        root / "pyproject.toml",
        root / "catalogue" / "catalogue_tests.json",
        root / "schemas" / "index.json",
    ]
    for path in required:
        if not path.exists():
            issues.append(AuditIssue("error", "MISSING_REQUIRED_FILE", str(path)))

    duplicate_descriptions: dict[str, list[str]] = {}
    for spec in specs:
        duplicate_descriptions.setdefault(spec.description, []).append(spec.test_id)
    duplicates = {key: value for key, value in duplicate_descriptions.items() if len(value) > 1}
    if duplicates:
        issues.append(
            AuditIssue(
                "warning",
                "DUPLICATE_DESCRIPTIONS",
                f"{len(duplicates)} descriptions répétées. Elles restent distinguées par leur contexte WP.",
            )
        )

    errors = [issue for issue in issues if issue.level == "error"]
    return AuditReport(
        ok=not errors,
        catalogue_entries=len(specs),
        work_packages=len(registry.by_wp()),
        engines=len({spec.engine for spec in specs}),
        datasets=len(SCHEMAS),
        issues=tuple(issues),
    )


def write_audit(report: AuditReport, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    return path
