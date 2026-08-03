from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

from .audit import audit_platform, write_audit
from .criteria import write_criteria_template
from .data_registry import DataRegistry, SCHEMAS
from .provenance import build_manifest
from .protocols import preregister, write_protocols
from .registry import Registry
from .report import write_csv_report, write_markdown_report
from .runner import RunOptions, run_campaign
from .synthetic_data import generate_all


@dataclass(frozen=True)
class BootstrapResult:
    workspace: Path
    tests: int
    datasets: int
    protocols: int
    counts: dict[str, int]


def bootstrap_workspace(
    package_root: Path,
    workspace: Path,
    *,
    seed: int = 0,
    synthetic: bool = False,
    oric_root: Path | None = None,
    max_priority: int | None = None,
) -> BootstrapResult:
    package_root = Path(package_root).resolve()
    workspace = Path(workspace).resolve()
    workspace.mkdir(parents=True, exist_ok=True)
    data_dir = workspace / "data"
    results_dir = workspace / "results" / "initial"
    protocol_dir = workspace / "protocols"
    prereg_dir = workspace / "preregistration"
    registry = Registry.load(package_root / "catalogue" / "catalogue_tests.json")
    specs = registry.all()
    if max_priority is not None:
        specs = [spec for spec in specs if spec.priority <= max_priority]

    if synthetic:
        generate_all(data_dir, seed=seed)
    else:
        data_dir.mkdir(parents=True, exist_ok=True)
        for schema in SCHEMAS.values():
            path = data_dir / schema.filename
            if not path.exists():
                path.write_text(",".join(schema.required_columns) + "\n", encoding="utf-8")

    protocol_paths = write_protocols(specs, protocol_dir)
    criteria_path = write_criteria_template(specs, prereg_dir / "criteria_template.csv")
    preregister(
        specs,
        prereg_dir / "catalogue_frozen.json",
        {"label": "bootstrap ORI-C complet", "synthetic": synthetic, "seed": seed},
    )

    campaign = run_campaign(
        specs,
        RunOptions(
            oric_root=oric_root,
            data_dir=data_dir,
            output_dir=results_dir,
            seed=seed,
            allow_missing_data=not synthetic,
            include_noncomputational=True,
            criteria_file=criteria_path,
        ),
    )
    campaign.save(results_dir)
    write_csv_report(campaign, results_dir / "results.csv")
    write_markdown_report(campaign, results_dir / "REPORT.md")
    audit = audit_platform(package_root)
    write_audit(audit, workspace / "AUDIT_PLATFORM.json")
    summary = {
        "workspace": str(workspace),
        "tests": len(specs),
        "datasets": len(SCHEMAS),
        "protocols": len(protocol_paths),
        "technical_counts": campaign.counts,
        "scientific_counts": campaign.scientific_counts,
        "synthetic": synthetic,
    }
    (workspace / "BOOTSTRAP_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    build_manifest(workspace, workspace / "MANIFEST.sha256.json")
    return BootstrapResult(workspace, len(specs), len(SCHEMAS), len(protocol_paths), campaign.counts)
