from __future__ import annotations

from pathlib import Path
from typing import Optional
import json

import typer
from rich.console import Console
from rich.table import Table

from .adapters.existing_oric import import_existing_data
from .audit import audit_platform, write_audit
from .config import load_campaign_config
from .criteria import write_criteria_template
from .data_registry import DataRegistry, SCHEMAS
from .models import ExecutionMode
from .pipeline import bootstrap_workspace
from .protocols import preregister, write_protocols
from .provenance import build_manifest, verify_manifest
from .registry import Registry
from .report import render_existing_result, write_csv_report, write_markdown_report
from .runner import RunOptions, run_campaign
from .synthetic_data import generate_all


app = typer.Typer(help="Plateforme complète de tests ORI-C")
console = Console()
PACKAGE_ROOT = Path(__file__).resolve().parents[2]


def _registry(catalog: Path | None) -> Registry:
    return Registry.load(catalog)


def _select_from_config(registry: Registry, config) -> list:
    if config.test_ids:
        specs = registry.select(test_ids=set(config.test_ids), max_priority=config.max_priority)
    elif config.work_packages:
        selected = []
        for wp in config.work_packages:
            selected.extend(registry.select(wp=wp, max_priority=config.max_priority))
        seen = set()
        specs = [spec for spec in selected if not (spec.test_id in seen or seen.add(spec.test_id))]
    elif config.select_all:
        specs = registry.all()
        if config.max_priority is not None:
            specs = [spec for spec in specs if spec.priority <= config.max_priority]
    else:
        specs = []
    return specs


@app.command("catalog")
def catalog_command(
    catalog: Optional[Path] = typer.Option(None, help="Catalogue JSON alternatif"),
    wp: Optional[str] = typer.Option(None, help="Filtrer un work package, ex. S1 ou WP-S1"),
) -> None:
    registry = _registry(catalog)
    specs = registry.select(wp=wp) if wp else registry.all()
    table = Table(title="Catalogue ORI-C")
    table.add_column("WP")
    table.add_column("Tests", justify="right")
    table.add_column("Automatisés", justify="right")
    table.add_column("Données", justify="right")
    table.add_column("Lab/Humain", justify="right")
    grouped: dict[str, list] = {}
    for spec in specs:
        grouped.setdefault(spec.wp, []).append(spec)
    for key in sorted(grouped):
        items = grouped[key]
        table.add_row(
            key,
            str(len(items)),
            str(sum(spec.mode == ExecutionMode.AUTOMATED for spec in items)),
            str(sum(spec.mode == ExecutionMode.DATA_REQUIRED for spec in items)),
            str(
                sum(
                    spec.mode
                    in {
                        ExecutionMode.LABORATORY,
                        ExecutionMode.HUMAN_REVIEW,
                        ExecutionMode.EXTERNAL_REPLICATION,
                    }
                    for spec in items
                )
            ),
        )
    console.print(table)
    console.print(f"Total : [bold]{len(specs)}[/bold] entrées")


@app.command("init-data")
def init_data_command(
    data_dir: Path = typer.Option(Path("data"), help="Dossier de données"),
    synthetic: bool = typer.Option(False, "--synthetic", help="Créer des données synthétiques de test"),
    overwrite: bool = typer.Option(False, help="Écraser les modèles existants"),
    seed: int = typer.Option(0),
) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)
    if synthetic:
        counts = generate_all(data_dir, seed=seed)
        console.print(f"[green]{len(counts)} jeux synthétiques créés dans {data_dir}[/green]")
        return
    for schema in SCHEMAS.values():
        path = data_dir / schema.filename
        if path.exists() and not overwrite:
            continue
        path.write_text(",".join(schema.required_columns) + "\n", encoding="utf-8")
    console.print(f"Modèles de données créés dans {data_dir}")


@app.command("import-existing")
def import_existing_command(
    oric_root: Path = typer.Argument(..., exists=True, file_okay=False),
    data_dir: Path = typer.Option(Path("data")),
) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)
    report = import_existing_data(oric_root, data_dir)
    console.print_json(json.dumps(report, ensure_ascii=False))


@app.command("validate-data")
def validate_data_command(
    data_dir: Path = typer.Option(Path("data")),
    dataset: Optional[str] = typer.Option(None, help="Nom d'un schéma précis"),
) -> None:
    registry = DataRegistry(data_dir)
    names = [dataset] if dataset else list(SCHEMAS)
    failures = 0
    table = Table(title="Validation des données")
    table.add_column("Jeu")
    table.add_column("Statut")
    table.add_column("Détail")
    for name in names:
        try:
            frame = registry.validate(name)
            table.add_row(name, "OK", f"{len(frame)} lignes")
        except Exception as exc:
            failures += 1
            table.add_row(name, "ABSENT/INVALIDE", str(exc))
    console.print(table)
    raise typer.Exit(code=1 if failures else 0)


@app.command("criteria-template")
def criteria_template_command(
    output: Path = typer.Option(Path("preregistration/criteria_template.csv")),
    catalog: Optional[Path] = typer.Option(None),
    wp: Optional[str] = typer.Option(None),
) -> None:
    registry = _registry(catalog)
    specs = registry.select(wp=wp) if wp else registry.all()
    write_criteria_template(specs, output)
    console.print(f"[green]Grille de critères créée : {output}[/green]")


@app.command("protocols")
def protocols_command(
    output_dir: Path = typer.Option(Path("protocols")),
    catalog: Optional[Path] = typer.Option(None),
    wp: Optional[str] = typer.Option(None),
) -> None:
    registry = _registry(catalog)
    specs = registry.select(wp=wp) if wp else registry.all()
    paths = write_protocols(specs, output_dir)
    console.print(f"[green]{len(paths)} protocoles écrits dans {output_dir}[/green]")


@app.command("preregister")
def preregister_command(
    output: Path = typer.Option(Path("preregistration/preregistration.json")),
    catalog: Optional[Path] = typer.Option(None),
    wp: Optional[str] = typer.Option(None),
    label: str = typer.Option("préenregistrement ORI-C"),
) -> None:
    registry = _registry(catalog)
    specs = registry.select(wp=wp) if wp else registry.all()
    preregister(specs, output, {"label": label, "wp": wp or "all"})
    console.print(f"[green]Préenregistrement gelé : {output}[/green]")


@app.command("run")
def run_command(
    all_tests: bool = typer.Option(False, "--all", help="Sélectionner tout le catalogue"),
    wp: Optional[str] = typer.Option(None, help="Work package"),
    test_id: list[str] = typer.Option([], "--test", help="Identifiant de test, répétable"),
    max_priority: Optional[int] = typer.Option(None, min=1, max=3),
    data_dir: Path = typer.Option(Path("data")),
    output_dir: Path = typer.Option(Path("results/latest")),
    oric_root: Optional[Path] = typer.Option(None, exists=True, file_okay=False),
    catalog: Optional[Path] = typer.Option(None),
    criteria_file: Optional[Path] = typer.Option(None),
    seed: int = typer.Option(0),
    allow_missing_data: bool = typer.Option(False),
    include_noncomputational: bool = typer.Option(True),
    real_data_only: bool = typer.Option(False, "--real-data-only", help="Interdire toute génération synthétique ou simulation"),
) -> None:
    registry = _registry(catalog)
    if all_tests:
        specs = registry.all()
        if max_priority is not None:
            specs = [spec for spec in specs if spec.priority <= max_priority]
    elif wp:
        specs = registry.select(wp=wp, max_priority=max_priority)
    elif test_id:
        specs = registry.select(test_ids=set(test_id), max_priority=max_priority)
    else:
        raise typer.BadParameter("Choisir --all, --wp ou --test")
    if not specs:
        raise typer.BadParameter("Aucun test sélectionné")
    options = RunOptions(
        oric_root=oric_root,
        data_dir=data_dir,
        output_dir=output_dir,
        seed=seed,
        allow_missing_data=allow_missing_data,
        include_noncomputational=include_noncomputational,
        criteria_file=criteria_file,
        real_data_only=real_data_only,
    )
    campaign = run_campaign(specs, options)
    campaign.save(output_dir)
    write_csv_report(campaign, output_dir / "results.csv")
    write_markdown_report(campaign, output_dir / "REPORT.md")
    console.print(f"[green]Exécution terminée : {output_dir}[/green]")
    console.print("Technique", campaign.counts)
    console.print("Scientifique", campaign.scientific_counts)
    fatal = campaign.counts.get("error", 0) + campaign.counts.get("fail", 0)
    raise typer.Exit(code=1 if fatal else 0)


@app.command("run-config")
def run_config_command(config_path: Path = typer.Argument(..., exists=True, dir_okay=False)) -> None:
    config = load_campaign_config(config_path)
    registry = Registry.load()
    specs = _select_from_config(registry, config)
    if not specs:
        raise typer.BadParameter("La configuration ne sélectionne aucun test")
    campaign = run_campaign(
        specs,
        RunOptions(
            oric_root=config.oric_root,
            data_dir=config.data_dir,
            output_dir=config.output_dir,
            seed=config.seed,
            allow_missing_data=config.allow_missing_data,
            include_noncomputational=config.include_noncomputational,
            criteria_file=config.criteria_file,
        ),
    )
    campaign.metadata.update({"campaign_name": config.name, **config.metadata})
    campaign.save(config.output_dir)
    write_csv_report(campaign, config.output_dir / "results.csv")
    write_markdown_report(campaign, config.output_dir / "REPORT.md")
    console.print(f"[green]Campagne {config.name} terminée : {config.output_dir}[/green]")
    console.print("Technique", campaign.counts)
    console.print("Scientifique", campaign.scientific_counts)
    fatal = campaign.counts.get("error", 0) + campaign.counts.get("fail", 0)
    raise typer.Exit(code=1 if fatal else 0)


@app.command("smoke")
def smoke_command(
    output_dir: Path = typer.Option(Path("results/smoke")),
    seed: int = typer.Option(0),
) -> None:
    registry = Registry.load()
    engines = {"core_formal", "intervention", "prebiotic_design", "antibiotic_design"}
    specs = [spec for spec in registry.all() if spec.engine in engines]
    campaign = run_campaign(
        specs,
        RunOptions(
            data_dir=Path("data"),
            output_dir=output_dir,
            seed=seed,
            allow_missing_data=True,
        ),
    )
    campaign.save(output_dir)
    write_csv_report(campaign, output_dir / "results.csv")
    write_markdown_report(campaign, output_dir / "REPORT.md")
    console.print(campaign.counts)
    raise typer.Exit(code=1 if campaign.counts.get("fail", 0) + campaign.counts.get("error", 0) else 0)


@app.command("demo-all")
def demo_all_command(
    workspace: Path = typer.Option(Path("demo_workspace")),
    seed: int = typer.Option(0),
) -> None:
    data_dir = workspace / "data"
    output_dir = workspace / "results"
    generate_all(data_dir, seed=seed)
    registry = Registry.load()
    campaign = run_campaign(
        registry.all(),
        RunOptions(
            data_dir=data_dir,
            output_dir=output_dir,
            seed=seed,
            allow_missing_data=False,
        ),
    )
    campaign.save(output_dir)
    write_csv_report(campaign, output_dir / "results.csv")
    write_markdown_report(campaign, output_dir / "REPORT.md")
    console.print(f"Démonstration complète : {output_dir}")
    console.print("Technique", campaign.counts)
    console.print("Scientifique", campaign.scientific_counts)


@app.command("bootstrap")
def bootstrap_command(
    workspace: Path = typer.Argument(...),
    synthetic: bool = typer.Option(False, "--synthetic"),
    seed: int = typer.Option(0),
    oric_root: Optional[Path] = typer.Option(None, exists=True, file_okay=False),
    max_priority: Optional[int] = typer.Option(None, min=1, max=3),
) -> None:
    result = bootstrap_workspace(
        PACKAGE_ROOT,
        workspace,
        seed=seed,
        synthetic=synthetic,
        oric_root=oric_root,
        max_priority=max_priority,
    )
    console.print(
        f"[green]Espace complet créé : {result.workspace} — {result.tests} entrées, "
        f"{result.datasets} schémas, {result.protocols} protocoles[/green]"
    )
    console.print(result.counts)


@app.command("audit")
def audit_command(
    output: Path = typer.Option(Path("audit/platform_audit.json")),
    catalog: Optional[Path] = typer.Option(None),
) -> None:
    report = audit_platform(PACKAGE_ROOT, catalog)
    write_audit(report, output)
    console.print_json(json.dumps(report.to_dict(), ensure_ascii=False))
    raise typer.Exit(code=0 if report.ok else 1)


@app.command("manifest")
def manifest_command(
    root: Path = typer.Argument(Path("."), exists=True, file_okay=False),
    output: Optional[Path] = typer.Option(None),
    verify: Optional[Path] = typer.Option(None, help="Manifeste existant à vérifier"),
) -> None:
    if verify:
        result = verify_manifest(root, verify)
        console.print_json(json.dumps(result, ensure_ascii=False))
        raise typer.Exit(code=0 if result["ok"] else 1)
    target = output or root / "MANIFEST.sha256.json"
    result = build_manifest(root, target)
    console.print(f"[green]{result['file_count']} fichiers inscrits dans {target}[/green]")


@app.command("report")
def report_command(run_dir: Path = typer.Argument(..., exists=True, file_okay=False)) -> None:
    output = render_existing_result(run_dir)
    console.print(f"Rapport écrit : {output}")


@app.command("status")
def status_command(
    catalog: Optional[Path] = typer.Option(None),
    data_dir: Path = typer.Option(Path("data")),
) -> None:
    registry = _registry(catalog)
    data = DataRegistry(data_dir)
    available = {name for name in SCHEMAS if data.exists(name)}
    table = Table(title="État de préparation ORI-C")
    table.add_column("WP")
    table.add_column("Tests")
    table.add_column("Jeux requis")
    table.add_column("Jeux disponibles")
    for wp, specs in sorted(registry.by_wp().items()):
        required = sorted({dataset for spec in specs for dataset in spec.required_datasets})
        have = sorted(set(required) & available)
        table.add_row(wp, str(len(specs)), ", ".join(required) or "—", f"{len(have)}/{len(required)}")
    console.print(table)


if __name__ == "__main__":
    app()
