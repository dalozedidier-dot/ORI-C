"""Noyau analytique et numérique du test interventionnel ORI-C.

Ce module isole le modèle utilisé par `test_interventionnel_ori_c.py` afin de
pouvoir le soumettre à des contrôles indépendants : solution stationnaire en
forme close, stabilité linéaire, seuil de lavage, cinétiques alternatives.

Le système est un chémostat à deux variables :

    dS/dt = D (S_in - S) - mu(S) P
    dP/dt = mu(S) P - (delta + l) P

où `l` est la seule variable d'intervention, le taux de perte du produit P.

Aucune fonction de ce module n'écrit sur le disque : il est directement
utilisable en test unitaire.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Callable, Literal

import numpy as np
from scipy.integrate import solve_ivp

Cinetique = Literal["monod", "masse_action", "haldane"]


@dataclass(frozen=True)
class Parametres:
    """Paramètres du modèle. Les valeurs par défaut sont celles du dossier."""

    mu_max: float = 1.0
    K_s: float = 1.0
    dilution: float = 0.25
    S_in: float = 10.0
    decay: float = 0.05
    leak_free: float = 0.25
    leak_membrane: float = 0.02
    S0: float = 1.0
    P0: float = 0.1
    K_i: float = 50.0  # inhibition par le substrat, cinétique de Haldane seule
    # 500 unités : au-delà des 298 requises pour amener le résidu transitoire
    # du mode lent sous 1e-9. La valeur historique de 80 était insuffisante.
    t_end: float = 500.0
    n_points: int = 2001


def croissance(cinetique: Cinetique, p: Parametres) -> Callable[[np.ndarray], np.ndarray]:
    """Renvoie mu(S) pour la cinétique demandée."""
    if cinetique == "monod":
        return lambda S: p.mu_max * S / (p.K_s + S)
    if cinetique == "masse_action":
        return lambda S: p.mu_max * S / p.K_s
    if cinetique == "haldane":
        return lambda S: p.mu_max * S / (p.K_s + S + S * S / p.K_i)
    raise ValueError(f"Cinétique inconnue : {cinetique}")


def derivee_croissance(cinetique: Cinetique, p: Parametres) -> Callable[[float], float]:
    """Renvoie mu'(S), nécessaire au jacobien."""
    if cinetique == "monod":
        return lambda S: p.mu_max * p.K_s / (p.K_s + S) ** 2
    if cinetique == "masse_action":
        return lambda S: p.mu_max / p.K_s
    if cinetique == "haldane":
        def d_haldane(S: float) -> float:
            den = p.K_s + S + S * S / p.K_i
            return p.mu_max * (p.K_s - S * S / p.K_i) / den**2
        return d_haldane
    raise ValueError(f"Cinétique inconnue : {cinetique}")


def perte_totale(leak: float, p: Parametres) -> float:
    """delta + l : le seul groupement par lequel l'intervention agit."""
    return p.decay + leak


def seuil_lavage(p: Parametres, cinetique: Cinetique = "monod") -> float:
    """Valeur de `leak` au-delà de laquelle P s'éteint (P* = 0).

    Le domaine de validité de l'affirmation causale est borné : au-delà de ce
    seuil, réduire la perte ne « retient » plus rien puisqu'il n'y a plus de P.
    """
    mu = croissance(cinetique, p)
    return float(mu(np.asarray(p.S_in)) - p.decay)


def etat_stationnaire(leak: float, p: Parametres, cinetique: Cinetique = "monod") -> tuple[float, float]:
    """Solution stationnaire exacte (S*, P*).

    Sous le seuil de lavage, l'équilibre intérieur vérifie mu(S*) = delta + l,
    puis P* = D (S_in - S*) / (delta + l). Au-delà, l'équilibre est le lavage
    (S* = S_in, P* = 0).
    """
    l = perte_totale(leak, p)
    if cinetique == "monod":
        if l >= p.mu_max:
            return p.S_in, 0.0
        S_eq = p.K_s * l / (p.mu_max - l)
    elif cinetique == "masse_action":
        S_eq = p.K_s * l / p.mu_max
    elif cinetique == "haldane":
        # p.mu_max S = l (K_s + S + S^2/K_i)  ->  (l/K_i) S^2 + (l - mu_max) S + l K_s = 0
        a, b, c = l / p.K_i, l - p.mu_max, l * p.K_s
        disc = b * b - 4 * a * c
        if disc < 0:
            return p.S_in, 0.0
        S_eq = (-b - np.sqrt(disc)) / (2 * a)  # branche stable, la plus basse
    else:
        raise ValueError(f"Cinétique inconnue : {cinetique}")

    if S_eq >= p.S_in:
        return p.S_in, 0.0
    return float(S_eq), float(p.dilution * (p.S_in - S_eq) / l)


def facteur_retention_analytique(
    leak_ref: float, leak_test: float, p: Parametres, cinetique: Cinetique = "monod"
) -> float:
    """P*(leak_test) / P*(leak_ref) en forme close."""
    _, P_ref = etat_stationnaire(leak_ref, p, cinetique)
    _, P_test = etat_stationnaire(leak_test, p, cinetique)
    if P_ref <= 0.0:
        return float("inf") if P_test > 0.0 else float("nan")
    return P_test / P_ref


def jacobien(leak: float, p: Parametres, cinetique: Cinetique = "monod") -> np.ndarray:
    """Jacobien évalué à l'équilibre intérieur."""
    S_eq, P_eq = etat_stationnaire(leak, p, cinetique)
    mu = croissance(cinetique, p)
    d_mu = derivee_croissance(cinetique, p)(S_eq)
    l = perte_totale(leak, p)
    return np.array(
        [
            [-p.dilution - d_mu * P_eq, -float(mu(np.asarray(S_eq)))],
            [d_mu * P_eq, float(mu(np.asarray(S_eq))) - l],
        ]
    )


def relaxation(leak: float, p: Parametres, cinetique: Cinetique = "monod") -> dict[str, float]:
    """Spectre du jacobien, temps de relaxation et horizon d'intégration requis.

    `t_requis_1e9` est la durée au-delà de laquelle le résidu transitoire du
    mode lent passe sous 1e-9 : c'est le critère qui manquait au script
    historique, dont la fenêtre de 80 unités laisse le compartiment sélectif
    en régime pré-asymptotique.
    """
    valeurs = np.linalg.eigvals(jacobien(leak, p, cinetique))
    partie_reelle = float(np.max(valeurs.real))
    tau = float("inf") if partie_reelle >= 0 else -1.0 / partie_reelle
    return {
        "lambda_max_reel": partie_reelle,
        "lambda_min_reel": float(np.min(valeurs.real)),
        "partie_imaginaire_max": float(np.max(np.abs(valeurs.imag))),
        "oscillant": bool(np.any(np.abs(valeurs.imag) > 1e-12)),
        "stable": bool(partie_reelle < 0),
        "tau_lent": tau,
        "t_requis_1e9": float(tau * np.log(1e9)) if np.isfinite(tau) else float("inf"),
    }


def simuler(
    leak: float,
    p: Parametres,
    *,
    t_end: float | None = None,
    n_points: int | None = None,
    y0: tuple[float, float] | None = None,
    methode: str = "LSODA",
    rtol: float = 1e-9,
    atol: float = 1e-11,
    cinetique: Cinetique = "monod",
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Intègre le système. Signature volontairement ouverte pour les balayages."""
    mu = croissance(cinetique, p)
    l = perte_totale(leak, p)

    def rhs(_t: float, y: np.ndarray) -> list[float]:
        S, P = y
        reaction = float(mu(np.asarray(S))) * P
        return [p.dilution * (p.S_in - S) - reaction, reaction - l * P]

    horizon = p.t_end if t_end is None else t_end
    points = p.n_points if n_points is None else n_points
    depart = (p.S0, p.P0) if y0 is None else y0
    solution = solve_ivp(
        rhs,
        (0.0, horizon),
        depart,
        t_eval=np.linspace(0.0, horizon, points),
        method=methode,
        rtol=rtol,
        atol=atol,
    )
    if not solution.success:
        raise RuntimeError(solution.message)
    S, P = solution.y
    return solution.t, S, P


def metriques_plateau(valeurs: np.ndarray, fraction: float = 0.10) -> dict[str, float]:
    """Reprend à l'identique la définition du script historique."""
    n_tail = max(20, int(len(valeurs) * fraction))
    tail = valeurs[-n_tail:]
    moyenne = float(np.mean(tail))
    ecart = float(np.std(tail))
    return {
        "mean": moyenne,
        "std": ecart,
        "cv": ecart / moyenne if moyenne > 0 else float("inf"),
        "relative_drift": float(abs(tail[-1] - tail[0]) / max(moyenne, 1e-12)),
    }


def parametres_avec(p: Parametres, **modifs: float) -> Parametres:
    """Copie immuable avec substitutions, pour les balayages."""
    return replace(p, **modifs)
