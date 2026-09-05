from __future__ import annotations

from pathlib import Path

import matplotlib

# This module exports PNG files and never opens interactive windows.
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def plot_orbital_series(earth: pd.DataFrame, output: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.plot(earth["time_years"] / 1000.0, earth["eccentricity"])
    ax.set_xlabel("Temps (ka)")
    ax.set_ylabel("Excentricité terrestre")
    ax.set_title("Série orbitale")
    fig.tight_layout()
    fig.savefig(output, dpi=160)
    plt.close(fig)


def plot_spectrum(spectrum: pd.DataFrame, output: Path) -> None:
    ordered = spectrum.sort_values("period_years")
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.plot(ordered["period_years"] / 1000.0, ordered["power"], label="Puissance")
    ax.plot(
        ordered["period_years"] / 1000.0,
        ordered["red_noise_threshold"],
        linestyle="--",
        label="Seuil bruit rouge",
    )
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Période (ka)")
    ax.set_ylabel("Puissance")
    ax.set_title("Spectre de l'excentricité")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output, dpi=160)
    plt.close(fig)


def plot_insolation_climate(insolation: pd.DataFrame, climate: pd.DataFrame, output: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.plot(insolation["time_years"] / 1000.0, insolation["insolation_w_m2"], label="Insolation")
    ax.set_xlabel("Temps (ka)")
    ax.set_ylabel("Insolation (W m⁻²)")
    twin = ax.twinx()
    twin.plot(climate["time_years"] / 1000.0, climate["ice_fraction"], label="Glace")
    twin.set_ylabel("Fraction glaciaire")
    ax.set_title("Forçage et réponse réduite")
    fig.tight_layout()
    fig.savefig(output, dpi=160)
    plt.close(fig)
