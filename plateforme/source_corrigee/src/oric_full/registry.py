from __future__ import annotations

from pathlib import Path
from typing import Iterable
import csv
import json

from .models import ExecutionMode, TestSpec


DEFAULT_CATALOG = Path(__file__).resolve().parent / "resources" / "catalogue_tests.json"


class Registry:
    def __init__(self, specs: Iterable[TestSpec]):
        self._specs = list(specs)
        ids = [s.test_id for s in self._specs]
        if len(ids) != len(set(ids)):
            duplicates = sorted({x for x in ids if ids.count(x) > 1})
            raise ValueError(f"Identifiants dupliqués: {duplicates}")

    @classmethod
    def load(cls, path: Path | None = None) -> "Registry":
        catalog_path = path or DEFAULT_CATALOG
        payload = json.loads(catalog_path.read_text(encoding="utf-8"))
        specs = []
        for item in payload:
            specs.append(
                TestSpec(
                    test_id=item["test_id"],
                    wp=item["wp"],
                    section=item["section"],
                    ordinal=int(item["ordinal"]),
                    description=item["description"],
                    mode=ExecutionMode(item["mode"]),
                    engine=item["engine"],
                    required_datasets=tuple(item.get("required_datasets", [])),
                    confirmatory=bool(item.get("confirmatory", False)),
                    priority=int(item.get("priority", 2)),
                    source_line=item.get("source_line"),
                )
            )
        return cls(specs)

    def all(self) -> list[TestSpec]:
        return list(self._specs)

    def select(
        self,
        *,
        wp: str | None = None,
        test_ids: set[str] | None = None,
        modes: set[ExecutionMode] | None = None,
        max_priority: int | None = None,
    ) -> list[TestSpec]:
        specs = self._specs
        if wp:
            normalized = wp.upper().replace("WP-", "")
            specs = [s for s in specs if s.wp.upper().replace("WP-", "") == normalized]
        if test_ids:
            specs = [s for s in specs if s.test_id in test_ids]
        if modes:
            specs = [s for s in specs if s.mode in modes]
        if max_priority is not None:
            specs = [s for s in specs if s.priority <= max_priority]
        return list(specs)

    def by_wp(self) -> dict[str, list[TestSpec]]:
        grouped: dict[str, list[TestSpec]] = {}
        for spec in self._specs:
            grouped.setdefault(spec.wp, []).append(spec)
        return grouped

    def write_csv(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        rows = [s.to_dict() for s in self._specs]
        for row in rows:
            row["required_datasets"] = ";".join(row["required_datasets"])
        if not rows:
            return
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
