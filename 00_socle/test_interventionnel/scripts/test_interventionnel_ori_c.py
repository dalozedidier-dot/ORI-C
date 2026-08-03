"""Test interventionnel ORI-C minimal, contrôlé et reproductible.

Deux systèmes partagent les mêmes constituants, conditions initiales,
apport de substrat et cinétique. La seule intervention est le taux de perte
du produit P : phase libre contre compartiment sélectif.

Ce modèle est illustratif. Il teste un principe causal dans un système défini ;
il ne constitue ni une observation empirique ni une preuve générale sur le vivant.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp

sys.path.insert(0, str(Path(__file__).resolve().parent))
from modele_ori_c import Parametres, etat_stationnaire, relaxation  # noqa: E402

# Tolérance de convergence : le plateau doit coïncider avec l'état stationnaire
# exact, et non seulement « varier peu » sur la fenêtre observée.
CONVERGENCE_TOL = 1e-6


@dataclass(frozen=True)
class Parameters:
    mu_max: float = 1.0
    K_s: float = 1.0
    dilution: float = 0.25
    S_in: float = 10.0
    decay: float = 0.05
    leak_free: float = 0.25
    leak_membrane: float = 0.02
    S0: float = 1.0
    P0: float = 0.1
    # Le mode lent du compartiment sélectif a un temps de relaxation de
    # 14,37 unités. Une fenêtre de 80 unités ne couvrait que 5,6 tau et
    # laissait un résidu transitoire de 3,8e-3 : le facteur mesuré valait
    # alors 4,4181 au lieu de 4,4439. Il faut tau * ln(1/tol), soit 298
    # unités pour une tolérance de 1e-9 ; 500 laisse une marge confortable.
    t_end: float = 500.0
    n_points: int = 2001


def simulate(leak_p: float, p: Parameters) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    def rhs(_t: float, y: np.ndarray) -> list[float]:
        S, P = y
        if S < 0 or P < 0:
            raise RuntimeError("Une concentration négative a été rencontrée.")
        mu = p.mu_max * S / (p.K_s + S)
        reaction = mu * P
        return [
            p.dilution * (p.S_in - S) - reaction,
            reaction - (p.decay + leak_p) * P,
        ]

    t_eval = np.linspace(0.0, p.t_end, p.n_points)
    solution = solve_ivp(
        rhs, (0.0, p.t_end), (p.S0, p.P0), t_eval=t_eval,
        method="LSODA", rtol=1e-9, atol=1e-11,
    )
    if not solution.success:
        raise RuntimeError(solution.message)
    S, P = solution.y
    return solution.t, S, P


def plateau_metrics(values: np.ndarray, fraction: float = 0.10) -> dict[str, float]:
    n_tail = max(20, int(len(values) * fraction))
    tail = values[-n_tail:]
    mean = float(np.mean(tail))
    std = float(np.std(tail))
    return {
        "mean": mean,
        "std": std,
        "cv": std / mean if mean > 0 else float("inf"),
        "relative_drift": float(abs(tail[-1] - tail[0]) / max(mean, 1e-12)),
    }


def result_paths() -> Path:
    script_dir = Path(__file__).resolve().parent
    results_dir = script_dir.parent / "resultats"
    results_dir.mkdir(parents=True, exist_ok=True)
    return results_dir


def main() -> None:
    p = Parameters()
    t, S_free, P_free = simulate(p.leak_free, p)
    _, S_compartment, P_compartment = simulate(p.leak_membrane, p)

    free = plateau_metrics(P_free)
    compartment = plateau_metrics(P_compartment)
    retention_ratio = compartment["mean"] / free["mean"]
    delta_pi = compartment["mean"] - free["mean"]
    delta_v = retention_ratio - 1.0

    # Référence analytique : l'équilibre intérieur vérifie mu(S*) = delta + l.
    # La comparer au plateau mesuré est le seul contrôle de convergence qui ne
    # dépende pas de la fenêtre d'observation.
    reference = Parametres(
        mu_max=p.mu_max, K_s=p.K_s, dilution=p.dilution, S_in=p.S_in, decay=p.decay,
        leak_free=p.leak_free, leak_membrane=p.leak_membrane, S0=p.S0, P0=p.P0,
        t_end=p.t_end, n_points=p.n_points,
    )
    _, P_free_exact = etat_stationnaire(p.leak_free, reference)
    _, P_compartment_exact = etat_stationnaire(p.leak_membrane, reference)
    exact_ratio = P_compartment_exact / P_free_exact
    gap_free = abs(free["mean"] - P_free_exact) / P_free_exact
    gap_compartment = abs(compartment["mean"] - P_compartment_exact) / P_compartment_exact
    gap_ratio = abs(retention_ratio - exact_ratio) / exact_ratio

    converged_free = gap_free < CONVERGENCE_TOL
    converged_compartment = gap_compartment < CONVERGENCE_TOL
    stable_free = free["cv"] < CONVERGENCE_TOL and free["relative_drift"] < CONVERGENCE_TOL
    stable_compartment = (
        compartment["cv"] < CONVERGENCE_TOL and compartment["relative_drift"] < CONVERGENCE_TOL
    )
    criterion_met = bool(
        stable_free and stable_compartment
        and converged_free and converged_compartment
        and delta_v > 0 and delta_pi > 0
    )

    results = {
        "status": "illustrative_controlled_model",
        "parameters": asdict(p),
        "intervention": {"variable": "loss_rate_of_P", "free": p.leak_free, "selective_compartment": p.leak_membrane},
        "plateau_free": free,
        "plateau_selective_compartment": compartment,
        "retention_ratio": retention_ratio,
        "delta_V": delta_v,
        "delta_Pi": delta_pi,
        "stable_free": stable_free,
        "stable_selective_compartment": stable_compartment,
        "analytic_reference": {
            "P_free": P_free_exact,
            "P_selective_compartment": P_compartment_exact,
            "retention_ratio": exact_ratio,
            "relative_gap_free": gap_free,
            "relative_gap_selective_compartment": gap_compartment,
            "relative_gap_retention_ratio": gap_ratio,
            "convergence_tolerance": CONVERGENCE_TOL,
            "converged_free": converged_free,
            "converged_selective_compartment": converged_compartment,
            "slow_relaxation_time_free": relaxation(p.leak_free, reference)["tau_lent"],
            "slow_relaxation_time_selective_compartment":
                relaxation(p.leak_membrane, reference)["tau_lent"],
        },
        "defined_causal_criterion_met": criterion_met,
        "scope_note": "Illustrative deterministic model; not an empirical or general biological proof.",
    }

    output_dir = result_paths()
    # newline="" empêche la traduction \n -> \r\n : les empreintes SHA-256 des
    # sorties textuelles doivent être identiques quel que soit le système.
    with (output_dir / "resultats_test_interventionnel_ori_c.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        np.savetxt(
            handle,
            np.column_stack((t, S_free, P_free, S_compartment, P_compartment)),
            delimiter=",",
            header="temps,S_phase_libre,P_phase_libre,S_compartiment,P_compartiment",
            comments="",
        )
    (output_dir / "metriques_test_interventionnel_ori_c.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n",
    )

    verdict = (
        "Le critère causal défini est satisfait dans ce modèle : la variation contrôlée "
        "de la perte de P modifie reproductiblement l'état stationnaire."
        if criterion_met else
        "Le critère causal défini n'est pas satisfait dans ce modèle."
    )
    report = [
        "TEST INTERVENTIONNEL ORI-C - MODÈLE CONTRÔLÉ ILLUSTRATIF",
        "Conditions initiales, apport de S et cinétique : identiques",
        f"Intervention unique : perte de P {p.leak_free:.3f} -> {p.leak_membrane:.3f}",
        f"Horizon d'intégration : {p.t_end:.0f} unités",
        f"Plateau P, phase libre : {free['mean']:.6f}",
        f"Plateau P, compartiment sélectif : {compartment['mean']:.6f}",
        f"Facteur de rétention : {retention_ratio:.4f}",
        f"Facteur de rétention, valeur analytique exacte : {exact_ratio:.4f}",
        f"Écart relatif au stationnaire exact : {gap_ratio:.2e}",
        f"Delta_V : {delta_v:.4f}",
        f"Delta_Pi : {delta_pi:.4f}",
        f"Plateaux stables : libre={stable_free}, compartiment={stable_compartment}",
        f"Plateaux convergés : libre={converged_free}, compartiment={converged_compartment}",
        f"Verdict interne : {verdict}",
        "Portée : test de cohérence interne d'un modèle défini, sans portée probante générale sur le vivant.",
    ]
    (output_dir / "rapport_test_interventionnel_ori_c.txt").write_text(
        "\n".join(report) + "\n", encoding="utf-8", newline="\n"
    )

    fig, ax = plt.subplots(figsize=(8.27, 6.2))
    ax.plot(t, P_free, linestyle="--", linewidth=1.8, label="Phase libre")
    ax.plot(t, P_compartment, linewidth=2.0, label="Compartiment sélectif")
    ax.axhline(free["mean"], linestyle=":", linewidth=1.0, label="Plateau libre")
    ax.axhline(compartment["mean"], linestyle=":", linewidth=1.0, label="Plateau compartiment")
    ax.set_title("Réponse stationnaire à une variation contrôlée de la perte de P")
    ax.set_xlabel("Temps, unités du modèle")
    ax.set_ylabel("Concentration de P")
    ax.grid(alpha=0.25)
    ax.legend(frameon=False)
    fig.text(
        0.5, 0.012,
        "Modèle déterministe illustratif : mêmes conditions et même cinétique ; seule la rétention de P varie.",
        ha="center", fontsize=7.2, color="#4A4A4A",
    )
    fig.tight_layout(rect=(0, 0.035, 1, 1))
    fig.savefig(output_dir / "test_interventionnel_ori_c.png", dpi=300, bbox_inches="tight",
                metadata={"Software": None})
    # Sans CreationDate, l'empreinte du PDF ne change plus d'une exécution à l'autre.
    fig.savefig(output_dir / "test_interventionnel_ori_c.pdf", bbox_inches="tight",
                metadata={"CreationDate": None, "Producer": None, "Creator": None})
    plt.close(fig)

    print("\n".join(report))


if __name__ == "__main__":
    main()
