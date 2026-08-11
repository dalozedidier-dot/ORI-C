#!/usr/bin/env python3
"""Pont minimal vers Chemical Organization Theory (COT).

Une organisation chimique exige au minimum clôture + auto-maintenance de masse.
Le dépôt ORI-C documentaire ne porte pas encore de matrice stœchiométrique ;
le diagnostic appliqué au corpus courant reste donc fail-closed.
"""
from __future__ import annotations
import numpy as np
from scipy.optimize import linprog

def is_closed(species:set[str], reactions:list[dict]) -> bool:
    for r in reactions:
        react=set(r['reactants'])
        if react <= species and not set(r['products']) <= species:
            return False
    return True

def mass_maintaining(species:set[str], reactions:list[dict], epsilon=1e-8) -> bool:
    """Test LP simplifié : un flux positif des réactions internes ne diminue aucune espèce.

    Les réactions doivent fournir `stoich`, mapping espèce -> coefficient net.
    """
    internal=[r for r in reactions if set(r['reactants'])<=species and set(r['products'])<=species]
    if not internal: return False
    names=sorted(species); S=np.array([[float(r['stoich'].get(s,0.0)) for r in internal] for s in names])
    # Cherche v >= epsilon, sum(v)=1 et S v >= 0.
    n=len(internal); c=np.zeros(n)
    res=linprog(c,A_ub=-S,b_ub=np.zeros(len(names)),A_eq=np.ones((1,n)),b_eq=np.ones(1),bounds=[(epsilon,None)]*n,method='highs')
    return bool(res.success)

def is_organization(species:set[str],reactions:list[dict]) -> bool:
    return is_closed(species,reactions) and mass_maintaining(species,reactions)
