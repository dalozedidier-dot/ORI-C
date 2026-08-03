"""Nulls spectraux LR04 contre bruit rouge AR(1), avec correction multiple."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "mpt_lr04_la2004.csv"
OUTPUT = ROOT / "results_stress" / "tests_reels" / "n_nulls_spectraux_lr04.json"
BANDS = {"41_ka": (35.0, 50.0), "100_ka": (80.0, 125.0)}
SEED = 20260802
DRAWS = 5000


def load() -> tuple[np.ndarray, np.ndarray]:
    age, values = [], []
    with DATA.open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            age.append(float(row["age_kyr_bp"]))
            values.append(float(row["d18o_permil"]))
    return np.asarray(age), np.asarray(values)


def band_fraction(series: np.ndarray, dt: float, limits: tuple[float, float]) -> float:
    centered = series - series.mean()
    power = np.abs(np.fft.rfft(centered)) ** 2
    frequency = np.fft.rfftfreq(len(series), d=dt)
    period = np.divide(1.0, frequency, out=np.full_like(frequency, np.inf), where=frequency > 0)
    mask = (period >= limits[0]) & (period <= limits[1])
    return float(power[mask].sum() / power[1:].sum())


def ar1_surrogates(series: np.ndarray, draws: int, rng: np.random.Generator) -> np.ndarray:
    centered = series - series.mean()
    rho = float(np.corrcoef(centered[:-1], centered[1:])[0, 1])
    rho = float(np.clip(rho, -0.995, 0.995))
    innovation_sd = float(centered.std(ddof=1) * np.sqrt(1.0 - rho * rho))
    output = np.empty((draws, len(series)))
    output[:, 0] = rng.normal(0.0, centered.std(ddof=1), draws)
    innovations = rng.normal(0.0, innovation_sd, (draws, len(series) - 1))
    for index in range(1, len(series)):
        output[:, index] = rho * output[:, index - 1] + innovations[:, index - 1]
    return output


def evaluate(series: np.ndarray, dt: float, rng: np.random.Generator) -> dict:
    nulls = ar1_surrogates(series, DRAWS, rng)
    report = {}
    for name, limits in BANDS.items():
        observed = band_fraction(series, dt, limits)
        simulated = np.asarray([band_fraction(row, dt, limits) for row in nulls])
        raw_p = float((np.sum(simulated >= observed) + 1) / (DRAWS + 1))
        report[name] = {
            "observed_power_fraction": observed,
            "null_mean": float(simulated.mean()),
            "null_ci_97.5": float(np.percentile(simulated, 97.5)),
            "p_raw": raw_p,
            "p_bonferroni_2_bands": min(1.0, 2.0 * raw_p),
        }
    return report


def main() -> int:
    age, values = load()
    order = np.argsort(age)
    age, values = age[order], values[order]
    dt = float(np.median(np.diff(age)))
    rng = np.random.default_rng(SEED)
    complete = evaluate(values, dt, rng)
    windows = []
    for low, high in ((0, 1200), (700, 1900), (1400, 2600)):
        mask = (age >= low) & (age <= high)
        windows.append({"age_ka": [low, high], "bands": evaluate(values[mask], dt, rng)})
    report = {
        "dataset": "LR04 real benthic d18O stack",
        "null": "Gaussian AR(1) fitted independently to each window",
        "draws_per_test": DRAWS,
        "seed": SEED,
        "complete_0_2600_ka": complete,
        "window_stability": windows,
        "scope": (
            "Ce test etablit si une bande excede un bruit rouge AR(1). Il ne demontre ni "
            "un mecanisme ORI-C ni une causalite astronomique."
        ),
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

