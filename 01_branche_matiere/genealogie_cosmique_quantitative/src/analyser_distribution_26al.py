#!/usr/bin/env python3
"""Distribution analytique de l'accessibilité 26Al, sans échantillonnage aléatoire."""
from __future__ import annotations

import math


HALF_LIFE_MYR = 0.717
Z95 = 1.959963984540054
THRESHOLDS = [0.25, 0.10, 0.01]


def analyse(complete: dict) -> dict:
    decay = math.log(2.0) / HALF_LIFE_MYR
    scenarios = {
        "canonique_homogene": 1.0,
        "reservoir_appauvri_facteur_3": 1.0 / 3.0,
        "reservoir_appauvri_facteur_4": 1.0 / 4.0,
    }
    events = []
    for event in complete["radiogenic_inventory"]:
        age = event["time_after_CAI_myr"]
        sigma = event["time_sigma_myr"]
        base = {
            "event": event["event"], "time_after_CAI_myr": age,
            "time_sigma_myr": sigma, "reservoir_scenarios": {},
        }
        for name, scale in scenarios.items():
            median = scale * math.exp(-decay * age)
            q025 = scale * math.exp(-decay * (age + Z95 * sigma))
            q975 = min(scale, scale * math.exp(-decay * max(0.0, age - Z95 * sigma)))
            base["reservoir_scenarios"][name] = {
                "remaining_fraction_median": median,
                "remaining_fraction_q025": q025,
                "remaining_fraction_q975": q975,
                "accessible_thresholds_at_median": [threshold for threshold in THRESHOLDS if median >= threshold],
                "accessible_thresholds_robust_q025": [threshold for threshold in THRESHOLDS if q025 >= threshold],
            }
        events.append(base)
    canonical_trace = [
        {
            "event": event["event"],
            "time_after_CAI_myr": event["time_after_CAI_myr"],
            "time_sigma_myr": event["time_sigma_myr"],
            "m_remaining_fraction_median": event["reservoir_scenarios"]["canonique_homogene"]["remaining_fraction_median"],
            "m_remaining_fraction_q025": event["reservoir_scenarios"]["canonique_homogene"]["remaining_fraction_q025"],
            "m_remaining_fraction_q975": event["reservoir_scenarios"]["canonique_homogene"]["remaining_fraction_q975"],
        }
        for event in events
    ]
    return {
        "schema": "oric.gc.26al-accessibility-distribution.v1",
        "status": "retrospective_analytic_sensitivity_not_preregistered",
        "quantity": "fraction de l'inventaire CAI de référence restant physiquement disponible",
        "m_trace": {
            "definition": "inventaire radiogénique résiduel continu dérivé des âges empiriques et de la demi-vie 26Al, avant discrétisation en classes P_acc",
            "status": "derived_physical_history_trace_from_empirical_ages",
            "canonical_reservoir_trace": canonical_trace,
            "distinction_from_P_acc": "m conserve la fraction continue résiduelle et son intervalle analytique; P_acc ne conserve que les seuils d'accessibilité franchis",
            "limitation": "trace dérivée sous modèle de décroissance et scénario de réservoir déclaré; elle n'est pas une mesure locale directe de 26Al dans chaque événement",
        },
        "half_life_myr": HALF_LIFE_MYR,
        "age_model": "normal approximation from published event age and sigma",
        "reservoir_history_model": "three declared sensitivity scenarios, not probabilities",
        "threshold_partition": THRESHOLDS,
        "events": events,
        "limits": [
            "ce calcul n'est ni une simulation thermique ni une probabilité de chauffage",
            "les facteurs 3 et 4 sont des scénarios de sensibilité tirés de l'hétérogénéité publiée, sans poids probabiliste",
            "la distribution conditionnelle complète P(Q26|t,H_reservoir) reste ouverte faute de distribution mesurée de H_reservoir",
        ],
    }
