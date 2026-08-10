#!/usr/bin/env python3
"""PID bivariée discrète selon la redondance I_min de Williams & Beer.

Ce module n'affirme pas que I_min est l'unique définition de la PID. Il fournit
une implémentation déterministe, explicitement identifiée, adaptée aux analyses
exploratoires reproductibles du dépôt.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from math import log2
from typing import Hashable, Iterable


def _prob(counter: Counter, n: int):
    return {k: v / n for k, v in counter.items()}


def mutual_information(x: list[Hashable], y: list[Hashable]) -> float:
    if len(x) != len(y) or not x:
        raise ValueError("x et y doivent avoir la même longueur non nulle")
    n = len(x)
    px, py = _prob(Counter(x), n), _prob(Counter(y), n)
    pxy = _prob(Counter(zip(x, y)), n)
    return sum(p * log2(p / (px[a] * py[b])) for (a, b), p in pxy.items())


def specific_information(source: list[Hashable], target: list[Hashable]) -> dict[Hashable, float]:
    """I(S;Y=y) au sens de Williams-Beer."""
    if len(source) != len(target) or not source:
        raise ValueError("source et target doivent avoir la même longueur non nulle")
    n = len(source)
    ps = _prob(Counter(source), n)
    py = _prob(Counter(target), n)
    psy = _prob(Counter(zip(source, target)), n)
    out: dict[Hashable, float] = {}
    ys = set(target)
    ss = set(source)
    for y in ys:
        val = 0.0
        for s in ss:
            p_sy = psy.get((s, y), 0.0)
            if p_sy == 0:
                continue
            p_s_given_y = p_sy / py[y]
            p_y_given_s = p_sy / ps[s]
            val += p_s_given_y * log2(p_y_given_s / py[y])
        out[y] = val
    return out


def pid_imin(x: list[Hashable], m: list[Hashable], y: list[Hashable]) -> dict[str, float]:
    """Décomposition à deux sources avec la redondance I_min.

    x: état/condition présente ; m: histoire ; y: cible future/réponse.
    """
    if not (len(x) == len(m) == len(y)) or not x:
        raise ValueError("x, m et y doivent avoir la même longueur non nulle")
    n = len(y)
    py = _prob(Counter(y), n)
    ix = mutual_information(x, y)
    im = mutual_information(m, y)
    joint = list(zip(x, m))
    ixm = mutual_information(joint, y)
    six = specific_information(x, y)
    sim = specific_information(m, y)
    redundancy = sum(py[v] * min(six[v], sim[v]) for v in py)
    unique_x = ix - redundancy
    unique_m = im - redundancy
    synergy = ixm - unique_x - unique_m - redundancy
    return {
        "I_X_Y_bits": ix,
        "I_M_Y_bits": im,
        "I_XM_Y_bits": ixm,
        "redundancy_Imin_bits": redundancy,
        "unique_X_bits": unique_x,
        "unique_M_history_bits": unique_m,
        "synergy_XM_bits": synergy,
    }
