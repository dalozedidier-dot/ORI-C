"""Figures de la campagne de stress."""

from __future__ import annotations

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from core import OUTPUT_ROOT

FIG = OUTPUT_ROOT / "figures"
GREY, BLUE, ORANGE, PURPLE, RED = "#A7A9AC", "#2B6CB0", "#D97706", "#8A5CF6", "#C53030"


def _style(axis):
    axis.grid(axis="y", color="#D9DDE3", linewidth=0.7)
    axis.set_axisbelow(True)
    for side in ("top", "right"):
        axis.spines[side].set_visible(False)


def figure_split_sensitivity() -> None:
    path = OUTPUT_ROOT / "mpt" / "a_split_sensitivity.csv"
    if not path.exists():
        return
    frame = pd.read_csv(path)
    figure, axis = plt.subplots(figsize=(9.5, 5.4))
    axis.axhline(0.05, color=RED, linestyle="--", linewidth=1.2,
                 label="seuil préenregistré (5 %)")
    axis.axhline(0.0, color="#333333", linewidth=0.9)
    axis.plot(frame["split_age_kyr"] / 1000.0, frame["gain_M2_vs_M1"], "o-",
              color=ORANGE, label="M2 contre M1")
    axis.plot(frame["split_age_kyr"] / 1000.0, frame["gain_M2_vs_M1P"], "s-",
              color=PURPLE, label="M2 contre M1P (contrôle à 9 paramètres)")
    axis.set_xlabel("Fenêtre de séparation calibration / prédiction (Ma)")
    axis.set_ylabel("Gain relatif de RMSE hors échantillon")
    axis.set_title("Sensibilité du gain de M2 à la fenêtre de séparation")
    axis.legend(frameon=False)
    _style(axis)
    figure.tight_layout()
    figure.savefig(FIG / "stress_split_sensitivity.png", dpi=180)
    plt.close(figure)


def figure_surrogate_null() -> None:
    path = OUTPUT_ROOT / "mpt" / "a_surrogate_null.csv"
    report = OUTPUT_ROOT / "mpt" / "a_report.json"
    if not path.exists() or not report.exists():
        return
    frame = pd.read_csv(path)
    data = json.loads(report.read_text(encoding="utf-8"))
    observed = None
    for entry in data.get("budget", {}).get(
        "budget_maximal_bornes_wide", {}
    ).get("gains", []):
        if entry["reference"] == "M1":
            observed = entry["rmse_gain"]

    figure, axes = plt.subplots(1, 2, figsize=(11.5, 4.6), sharey=True)
    for axis, kind, title in zip(
        axes, ("cible", "forcage"),
        ("Nul : cible LR04 à phases aléatoires",
         "Nul : forçage La2004 à phases aléatoires"),
    ):
        subset = frame.loc[frame["null_kind"] == kind, "gain_M2_vs_M1"]
        axis.hist(subset, bins=20, color=GREY, edgecolor="#333333", linewidth=0.5)
        axis.axvline(0.05, color=RED, linestyle="--", linewidth=1.2,
                     label="seuil 5 %")
        if observed is not None:
            axis.axvline(observed, color=ORANGE, linewidth=1.8,
                         label=f"gain observé ({observed:.3f})")
        axis.set_title(title, fontsize=10)
        axis.set_xlabel("Gain de RMSE de M2 sur M1")
        _style(axis)
    axes[0].set_ylabel("Nombre de tirages")
    axes[0].legend(frameon=False, fontsize=9)
    figure.suptitle("Distribution nulle du gain de M2")
    figure.tight_layout()
    figure.savefig(FIG / "stress_surrogate_null.png", dpi=180)
    plt.close(figure)


def figure_relaxation() -> None:
    path = OUTPUT_ROOT / "exoplanet" / "b_relaxation.csv"
    if not path.exists():
        return
    frame = pd.read_csv(path)
    variables = frame["variable"].unique()
    figure, axes = plt.subplots(1, len(variables), figsize=(15.0, 4.2),
                                sharex=True)
    for axis, variable in zip(np.atleast_1d(axes), variables):
        subset = frame.loc[frame["variable"] == variable].sort_values(
            "final_hold_myr"
        )
        threshold = float(subset["materiality_threshold"].iloc[0])
        axis.semilogy(subset["final_hold_myr"],
                      subset["median_delta_M2"].clip(lower=1e-18), "o-",
                      color=ORANGE, label="M2")
        axis.semilogy(subset["final_hold_myr"],
                      subset["median_delta_ablated"].clip(lower=1e-18), "s-",
                      color=PURPLE, label="M2 sans mémoire")
        axis.axhline(threshold, color=RED, linestyle="--", linewidth=1.1,
                     label="seuil de matérialité")
        axis.axvline(10.0, color="#333333", linestyle=":", linewidth=1.0,
                     label="palier livré")
        axis.set_title(variable, fontsize=10)
        axis.set_xlabel("Durée du palier final (Ma)")
        _style(axis)
    np.atleast_1d(axes)[0].set_ylabel("|A − B| médian")
    np.atleast_1d(axes)[0].legend(frameon=False, fontsize=8)
    figure.suptitle(
        "La dépendance au chemin s'efface quand le forçage final est maintenu"
    )
    figure.tight_layout()
    figure.savefig(FIG / "stress_relaxation.png", dpi=180)
    plt.close(figure)


def figure_capacity() -> None:
    path = OUTPUT_ROOT / "independence" / "c_report.json"
    if not path.exists():
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    capacity = data.get("capacity")
    if not capacity:
        return
    target = capacity["observed_power_ratio"]
    models = [name for name in ("M1", "M1P", "M2") if name in capacity]
    values = [capacity[name]["best_achievable_power_ratio"] for name in models]

    figure, axis = plt.subplots(figsize=(7.6, 5.0))
    bars = axis.bar(models, values, color=[BLUE, PURPLE, ORANGE],
                    edgecolor="#333333", linewidth=0.5)
    axis.axhline(target, color="#222222", linewidth=1.6, label="LR04 observé")
    axis.axhspan(target / 2.0, target * 2.0, color="#E7F4EA", alpha=0.8,
                 label="tolérance facteur 2")
    axis.set_yscale("log")
    axis.set_ylabel("Rapport de puissance 80–120 ka / 39–43 ka")
    axis.set_title(
        "Rapport spectral maximal atteignable en optimisant directement ce critère"
    )
    for bar, value in zip(bars, values):
        axis.text(bar.get_x() + bar.get_width() / 2, value * 1.2,
                  f"{value:.3g}", ha="center", fontsize=9)
    axis.legend(frameon=False)
    _style(axis)
    figure.tight_layout()
    figure.savefig(FIG / "stress_spectral_capacity.png", dpi=180)
    plt.close(figure)


def figure_forcing_robustness() -> None:
    path = OUTPUT_ROOT / "independence" / "c_forcing_robustness.csv"
    if not path.exists():
        return
    frame = pd.read_csv(path).sort_values("gain_M2_vs_M1")
    positions = np.arange(len(frame))
    figure, axis = plt.subplots(figsize=(10.5, 5.6))
    axis.barh(positions - 0.2, frame["gain_M2_vs_M1"], 0.38, color=ORANGE,
              label="M2 contre M1", edgecolor="#333333", linewidth=0.4)
    axis.barh(positions + 0.2, frame["gain_M2_vs_M1P"], 0.38, color=PURPLE,
              label="M2 contre M1P", edgecolor="#333333", linewidth=0.4)
    axis.axvline(0.05, color=RED, linestyle="--", linewidth=1.2,
                 label="seuil 5 %")
    axis.axvline(0.0, color="#333333", linewidth=0.9)
    axis.set_yticks(positions, frame["forcing"])
    axis.set_xlabel("Gain relatif de RMSE hors échantillon")
    axis.set_title("Dépendance du verdict à la définition du forçage astronomique")
    axis.legend(frameon=False)
    axis.grid(axis="x", color="#D9DDE3", linewidth=0.7)
    axis.set_axisbelow(True)
    figure.tight_layout()
    figure.savefig(FIG / "stress_forcing_robustness.png", dpi=180)
    plt.close(figure)


def figure_regime_scan() -> None:
    path = OUTPUT_ROOT / "exoplanet" / "b_final_regime_scan.csv"
    if not path.exists():
        return
    frame = pd.read_csv(path)
    pivot = frame.pivot(index="final_eccentricity",
                        columns="final_obliquity_deg",
                        values="delta10_temperature_k")
    figure, axes = plt.subplots(1, 2, figsize=(12.5, 4.8))
    for axis, values, title in (
        (axes[0], pivot, "Écart A−B de température au palier livré (10 Ma)"),
        (axes[1],
         frame.pivot(index="final_eccentricity",
                     columns="final_obliquity_deg",
                     values="attractor_ice_mean"),
         "Fraction de glace de l'attracteur unique"),
    ):
        image = axis.imshow(values.to_numpy(), origin="lower", aspect="auto",
                            cmap="magma")
        axis.set_xticks(range(len(values.columns)),
                        [f"{c:g}" for c in values.columns], fontsize=8)
        axis.set_yticks(range(len(values.index)),
                        [f"{i:g}" for i in values.index], fontsize=8)
        axis.set_xlabel("Obliquité finale (°)")
        axis.set_ylabel("Excentricité finale")
        axis.set_title(title, fontsize=10)
        figure.colorbar(image, ax=axis)
    figure.suptitle(
        "Aucun régime de forçage final ne rend l'écart matériel ni permanent"
    )
    figure.tight_layout()
    figure.savefig(FIG / "stress_final_regime_scan.png", dpi=180)
    plt.close(figure)


def main() -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    for function in (
        figure_split_sensitivity, figure_surrogate_null, figure_relaxation,
        figure_capacity, figure_forcing_robustness, figure_regime_scan,
    ):
        try:
            function()
            print(f"  {function.__name__} ok")
        except Exception as error:  # pragma: no cover - diagnostic
            print(f"  {function.__name__} ÉCHEC : {error}")


if __name__ == "__main__":
    main()
