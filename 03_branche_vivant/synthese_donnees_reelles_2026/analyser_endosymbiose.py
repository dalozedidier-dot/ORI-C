#!/usr/bin/env python3
from pathlib import Path
import hashlib
import json
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DATA = ROOT / "plateforme" / "campagne_maximale_reelle" / "data"
OUT = HERE / "ENDOSYMBIOSE_RETENTION_MODULAIRE.json"

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

events_path = DATA / "endosymbiosis_events.csv"
hmm_path = DATA / "endosymbiont_hmm_presence_absence.csv"
events = pd.read_csv(events_path)
hmm = pd.read_csv(hmm_path)

rows = []
for _, row in events.iterrows():
    for section, value in json.loads(row.section_retention_json).items():
        rows.append({
            "event_id": row.event_id,
            "genome_retention": float(row.genome_retention_proxy),
            "section": section,
            "retention": float(value),
        })

long = pd.DataFrame(rows)
wide = long.pivot(index="event_id", columns="section", values="retention")
q1 = events.genome_retention_proxy.quantile(0.25)
q3 = events.genome_retention_proxy.quantile(0.75)

section_stats = {}
for section, group in long.groupby("section"):
    rho, p_value = stats.spearmanr(group.genome_retention, group.retention)
    section_stats[section] = {
        "n": len(group),
        "mean": float(group.retention.mean()),
        "median": float(group.retention.median()),
        "spearman_vs_genome_retention": float(rho),
        "spearman_p": float(p_value),
        "low_genome_retention_quartile_mean": float(
            group[group.genome_retention <= q1].retention.mean()
        ),
        "high_genome_retention_quartile_mean": float(
            group[group.genome_retention >= q3].retention.mean()
        ),
    }

paired = {}
for section in ["PMF", "envelope", "replication", "transcription"]:
    difference = wide.translation - wide[section]
    _, p_value = stats.wilcoxon(difference, alternative="greater")
    paired[section] = {
        "translation_minus_section_mean": float(difference.mean()),
        "median": float(difference.median()),
        "translation_greater_n": int((difference > 0).sum()),
        "equal_n": int((difference == 0).sum()),
        "wilcoxon_p_one_sided": float(p_value),
    }

friedman_stat, friedman_p = stats.friedmanchisquare(
    *(wide[column] for column in ["PMF", "envelope", "replication", "transcription", "translation"])
)
result = {
    "schema": "oric.endosymbiosis-modular-retention.v1",
    "events": len(events),
    "hmm_rows": len(hmm),
    "source_events": "plateforme/campagne_maximale_reelle/data/endosymbiosis_events.csv",
    "source_events_sha256": sha256(events_path),
    "source_hmm": "plateforme/campagne_maximale_reelle/data/endosymbiont_hmm_presence_absence.csv",
    "source_hmm_sha256": sha256(hmm_path),
    "analysis_status": "retrospective_cross_sectional_structural_analysis",
    "section_retention": section_stats,
    "paired_translation_retention": paired,
    "friedman_across_five_modules": {
        "statistic": float(friedman_stat),
        "p": float(friedman_p),
    },
    "interpretation": (
        "Genome reduction is strongly non-uniform across functional modules. Translation "
        "is retained disproportionately while envelope, PMF and replication are lost earlier. "
        "This is a structural constraint pattern, not evidence of temporal memory H or an isolated trace m."
    ),
    "counts_for_strict_invariant": False,
}
OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
print(f"{len(events)} events, {len(hmm)} HMM calls -> {OUT.relative_to(ROOT)}")
