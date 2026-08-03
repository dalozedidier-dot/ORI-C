from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class CampaignConfig:
    name: str = "oric-campaign"
    select_all: bool = True
    work_packages: tuple[str, ...] = ()
    test_ids: tuple[str, ...] = ()
    max_priority: int | None = None
    seed: int = 0
    allow_missing_data: bool = False
    include_noncomputational: bool = True
    data_dir: Path = Path("data")
    output_dir: Path = Path("results/latest")
    oric_root: Path | None = None
    criteria_file: Path | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


def _resolve(base: Path, value: str | None) -> Path | None:
    if value in {None, ""}:
        return None
    path = Path(str(value))
    return path if path.is_absolute() else (base / path).resolve()


def load_campaign_config(path: Path) -> CampaignConfig:
    path = Path(path)
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    base = path.parent.resolve()
    selection = payload.get("selection", {}) or {}
    execution = payload.get("execution", {}) or {}
    paths = payload.get("paths", {}) or {}
    max_priority = selection.get("max_priority")
    if max_priority is not None:
        max_priority = int(max_priority)
        if max_priority not in {1, 2, 3}:
            raise ValueError("max_priority doit être 1, 2 ou 3")
    return CampaignConfig(
        name=str(payload.get("name", path.stem)),
        select_all=bool(selection.get("all", True)),
        work_packages=tuple(str(x) for x in selection.get("work_packages", []) or []),
        test_ids=tuple(str(x) for x in selection.get("test_ids", []) or []),
        max_priority=max_priority,
        seed=int(execution.get("seed", 0)),
        allow_missing_data=bool(execution.get("allow_missing_data", False)),
        include_noncomputational=bool(execution.get("include_noncomputational", True)),
        data_dir=_resolve(base, paths.get("data_dir")) or Path("data"),
        output_dir=_resolve(base, paths.get("output_dir")) or Path("results/latest"),
        oric_root=_resolve(base, paths.get("oric_root")),
        criteria_file=_resolve(base, paths.get("criteria_file")),
        metadata=dict(payload.get("metadata", {}) or {}),
    )
