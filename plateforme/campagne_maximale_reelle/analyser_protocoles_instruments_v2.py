#!/usr/bin/env python3
"""Exécute les sept protocoles Instruments V2 gelés le 17 août 2026.

Les résultats sur les données déjà ouvertes sont des calibrations rétrospectives.
Aucun résultat de ce module n'accorde automatiquement de crédit §XIV.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.spatial.distance import jensenshannon
from scipy.stats import wilcoxon
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DATA = HERE / "data"
PROTOCOL_DIR = ROOT / "plan_directeur" / "campagne_centrale_2026_08_11" / "PROTOCOLES_INSTRUMENTS_V2"
CURRENT_RESULTS = HERE / "resultats_consolides" / "DONNEES_SOUS_EXPLOITEES.json"
DEFAULT_OUTPUT = HERE / "resultats_consolides" / "PROTOCOLES_INSTRUMENTS_V2_CALIBRATION.json"
SEED = 20260817


def _r(x: Any, digits: int = 12) -> Any:
    if isinstance(x, (float, np.floating)):
        if not math.isfinite(float(x)):
            return None
        return round(float(x), digits)
    if isinstance(x, (int, np.integer)):
        return int(x)
    return x


def _protocol(pid: str) -> dict:
    return json.loads((PROTOCOL_DIR / f"{pid}.json").read_text(encoding="utf-8"))


def _ridge_oof(data: pd.DataFrame, numeric: list[str], categorical: list[str], target: str, group: str) -> np.ndarray:
    pred = np.full(len(data), np.nan)
    splitter = GroupKFold(n_splits=5)
    for train, test in splitter.split(data, groups=data[group]):
        transformers = []
        if numeric:
            transformers.append(("num", Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]), numeric))
        if categorical:
            transformers.append(("cat", OneHotEncoder(handle_unknown="ignore"), categorical))
        model = Pipeline([("features", ColumnTransformer(transformers)), ("ridge", Ridge(alpha=1.0))])
        model.fit(data.iloc[train], data.iloc[train][target])
        pred[test] = model.predict(data.iloc[test])
    return pred


def _bootstrap_mean_ci(values: np.ndarray, repeats: int = 4000, seed_offset: int = 0) -> list[float]:
    values = np.asarray(values, dtype=float)
    rng = np.random.default_rng(SEED + seed_offset)
    out = np.empty(repeats, dtype=float)
    for i in range(repeats):
        out[i] = rng.choice(values, size=len(values), replace=True).mean()
    return [_r(x) for x in np.quantile(out, [0.025, 0.975])]


def run_hmr_x_ladder() -> dict:
    cfg = _protocol("HMR-X-LADDER-001")
    cycles = pd.read_csv(DATA / "antibiotic_cycles.csv")
    measurements = pd.read_csv(DATA / "antibiotic_measurements.csv")
    table = cycles.merge(measurements, on=["lineage_id", "cycle"], how="inner").sort_values(["lineage_id", "cycle"]).copy()
    table["previous_survival"] = table.groupby("lineage_id")["survival"].shift(1)
    table["next_survival"] = table.groupby("lineage_id")["survival"].shift(-1)
    use = table.dropna(subset=["survival", "previous_survival", "next_survival", "dose", "duration", "recovery_duration"]).copy()
    y = use["next_survival"].to_numpy(float)
    rungs = []
    for i, rung in enumerate(cfg["state_ladder"]):
        pred_x = _ridge_oof(use, rung["numeric"], rung["categorical"], "next_survival", "lineage_id")
        pred_xh = _ridge_oof(use, rung["numeric"] + [cfg["history_feature"]], rung["categorical"], "next_survival", "lineage_id")
        ex = y - pred_x
        exh = y - pred_xh
        rmse_x = float(np.sqrt(np.mean(ex ** 2)))
        rmse_xh = float(np.sqrt(np.mean(exh ** 2)))
        paired_gain = ex ** 2 - exh ** 2
        relative = (rmse_x - rmse_xh) / rmse_x * 100.0
        ci = _bootstrap_mean_ci(paired_gain, seed_offset=i)
        rungs.append({
            "id": rung["id"], "rows": len(use), "lineages": use["lineage_id"].nunique(),
            "RMSE_X": _r(rmse_x), "RMSE_X_plus_H": _r(rmse_xh),
            "relative_RMSE_gain_percent": _r(relative),
            "paired_squared_error_gain_mean": _r(np.mean(paired_gain)),
            "paired_squared_error_gain_bootstrap95": ci,
            "history_survives_frozen_future_rule": bool(relative >= cfg["future_survival_rule"]["minimum_relative_gain_percent"] and ci[0] > cfg["future_survival_rule"]["paired_squared_error_gain_bootstrap95_lower_must_exceed"]),
        })
    gains = [r["relative_RMSE_gain_percent"] for r in rungs]
    return {
        "protocol_id": cfg["id"], "status": "retrospective_calibration", "rows_common": len(use),
        "rungs": rungs,
        "gain_attenuation_X0_to_X2_pp": _r(gains[0] - gains[-1]),
        "gain_monotonically_decreases_with_X_richness": bool(all(a >= b for a, b in zip(gains, gains[1:]))),
        "richest_X_history_survives": rungs[-1]["history_survives_frozen_future_rule"],
        "section_XIV_credit": False,
    }


def _add_ancestor_yields(table: pd.DataFrame, max_depth: int) -> pd.DataFrame:
    out = table.copy()
    lookup = out.set_index("lineage_id")[["parent_id", "yield"]].to_dict("index")
    for depth in range(1, max_depth + 1):
        vals = []
        for row in out.itertuples():
            pid = row.parent_id
            value = np.nan
            for _ in range(depth):
                if pd.isna(pid) or pid not in lookup:
                    value = np.nan
                    break
                rec = lookup[pid]
                value = rec["yield"]
                pid = rec["parent_id"]
            vals.append(value)
        out[f"ancestor_yield_d{depth}"] = vals
    return out


def run_h_depth_ladder() -> dict:
    cfg = _protocol("H-DEPTH-LADDER-001")
    table = _add_ancestor_yields(pd.read_csv(DATA / "prebiotic_lineages.csv"), max(cfg["ancestor_depths"]))
    required = [f"ancestor_yield_d{d}" for d in cfg["ancestor_depths"]]
    use = table.dropna(subset=["yield", "source_file"] + required).copy()
    base_num = cfg["context_numeric"]
    cat = cfg["context_categorical"]
    y = use["yield"].to_numpy(float)
    pred = _ridge_oof(use, base_num, cat, "yield", "source_file")
    previous_rmse = float(np.sqrt(np.mean((y - pred) ** 2)))
    levels = [{"depth": 0, "RMSE": _r(previous_rmse), "incremental_gain_percent": None}]
    effective = 0
    threshold = cfg["future_depth_rule"]["minimum_incremental_gain_percent"]
    for depth in cfg["ancestor_depths"]:
        nums = base_num + [f"ancestor_yield_d{d}" for d in range(1, depth + 1)]
        pred = _ridge_oof(use, nums, cat, "yield", "source_file")
        rmse = float(np.sqrt(np.mean((y - pred) ** 2)))
        gain = (previous_rmse - rmse) / previous_rmse * 100.0
        if gain >= threshold:
            effective = depth
        levels.append({"depth": depth, "RMSE": _r(rmse), "incremental_gain_percent": _r(gain)})
        previous_rmse = rmse
    return {
        "protocol_id": cfg["id"], "status": "retrospective_calibration", "rows_common_through_depth4": len(use),
        "source_files": use["source_file"].nunique(), "levels": levels,
        "effective_depth_at_2pct_increment": effective,
        "deeper_than_parent_adds_2pct_increment": bool(any((x["incremental_gain_percent"] or -1e9) >= threshold for x in levels if x["depth"] >= 2)),
        "section_XIV_credit": False,
    }


def run_pacc_vector() -> dict:
    cfg = _protocol("PACC-VECTOR-001")
    current = json.loads(CURRENT_RESULTS.read_text(encoding="utf-8"))
    source = current["analyses"]["santos_lopez_cross_resistance"]
    by_pair = source["by_evolved_and_tested_drug"]
    lo, hi = cfg["neutral_band_fold"]
    routes = {}
    vectors = {}
    for evolved in cfg["routes"]:
        folds = np.asarray([float(by_pair[f"{evolved}->{tested}"]["median_fold_day12_over_day0"]) for tested in cfg["challenge_order"]], dtype=float)
        vec = np.log2(folds)
        vectors[evolved] = vec
        labels = ["expanded" if x > hi else "contracted" if x < lo else "near_neutral" for x in folds]
        routes[evolved] = {
            "median_fold_vector": [_r(x) for x in folds], "log2_fold_vector": [_r(x) for x in vec],
            "direction_labels": labels, "anisotropy_log2_span": _r(np.ptp(vec)),
            "max_over_min_fold_ratio": _r(np.max(folds) / np.min(folds)), "vector_L2_norm": _r(np.linalg.norm(vec)),
        }
    a, b = (vectors[x] for x in cfg["routes"])
    cosine = float(np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b)))
    distance = float(np.linalg.norm(a-b))
    scalar = float(source["collateral_response_median_fold"])
    mixed = any("expanded" in r["direction_labels"] and "contracted" in r["direction_labels"] for r in routes.values())
    return {
        "protocol_id": cfg["id"], "status": "retrospective_proxy_geometry_calibration", "routes": routes,
        "route_cosine_similarity": _r(cosine), "route_L2_distance_log2": _r(distance),
        "scalar_collateral_median_fold": _r(scalar), "scalar_neutral": bool(lo <= scalar <= hi),
        "mixed_expansion_and_contraction_within_route": mixed,
        "scalar_masking_detected": bool(lo <= scalar <= hi and mixed),
        "causal_Pacc_measured": False, "section_XIV_credit": False,
    }


def _thermo_grid_summary(table: pd.DataFrame, composition: str) -> dict:
    comp = table[(table["state"] == "cr") & (table["composition"] == composition)].copy()
    records = []
    for (T,P), group in comp.groupby(["temperature","pressure"]):
        ranked = group.sort_values("gibbs_energy")
        if len(ranked) < 2:
            continue
        records.append({"temperature":float(T),"pressure":float(P),"winner":str(ranked.iloc[0]["phase"]),"runner":str(ranked.iloc[1]["phase"]),"gap":float(ranked.iloc[1]["gibbs_energy"]-ranked.iloc[0]["gibbs_energy"])})
    grid = pd.DataFrame(records)
    index = {(r.temperature,r.pressure):r for r in grid.itertuples()}
    Ts = sorted(grid["temperature"].unique()); Ps = sorted(grid["pressure"].unique())
    boundary_points=set(); pairs=[]
    for i,T in enumerate(Ts):
        for j,P in enumerate(Ps):
            if (T,P) not in index: continue
            neighbors=[]
            if i+1<len(Ts): neighbors.append((Ts[i+1],P))
            if j+1<len(Ps): neighbors.append((T,Ps[j+1]))
            for key in neighbors:
                if key not in index: continue
                a=index[(T,P)]; b=index[key]
                if a.winner != b.winner:
                    boundary_points.add((T,P)); boundary_points.add(key)
                    pairs.append(tuple(sorted((a.winner,b.winner))))
    grid["boundary"]=[(r.temperature,r.pressure) in boundary_points for r in grid.itertuples()]
    bmed=float(grid.loc[grid["boundary"],"gap"].median()); imed=float(grid.loc[~grid["boundary"],"gap"].median())
    from collections import Counter
    pair_counts={" | ".join(k):int(v) for k,v in sorted(Counter(pairs).items(), key=lambda kv:(-kv[1],kv[0]))}
    return {"winner_phases":sorted(grid["winner"].unique()),"grid_points":len(grid),"boundary_edge_count":len(pairs),"boundary_point_count":int(grid["boundary"].sum()),"phase_pair_counts":pair_counts,"boundary_median_gap":_r(bmed),"interior_median_gap":_r(imed),"boundary_to_interior_gap_ratio":_r(bmed/imed)}


def run_threshold_surface() -> dict:
    cfg=_protocol("THRESHOLD-SURFACE-001")
    table=pd.read_csv(DATA/"thermochemical_phases.csv")
    comps={c:_thermo_grid_summary(table,c) for c in cfg["priority_compositions"]}
    rule=cfg["candidate_rule"]
    for rec in comps.values():
        rec["boundary_coherence_candidate"] = bool(rec["boundary_edge_count"] >= rule["minimum_boundary_edges"] and rec["boundary_to_interior_gap_ratio"] <= rule["maximum_boundary_to_interior_gap_ratio"])
    return {"protocol_id":cfg["id"],"status":"retrospective_surface_calibration","compositions":comps,"all_priority_candidates_coherent":all(r["boundary_coherence_candidate"] for r in comps.values()),"full_multiphase_equilibrium_solved":False,"section_XIV_credit":False}


def _cumulative_horizons(times: np.ndarray, errors: np.ndarray, budgets: list[float]) -> dict:
    cumulative=np.sqrt(np.cumsum(errors**2)/np.arange(1,len(errors)+1))
    out={}
    for budget in budgets:
        hit=np.flatnonzero(cumulative>=budget)
        out[str(budget)] = None if len(hit)==0 else _r(abs(times[hit[0]]),6)
    return out


def run_orbit_validity_envelope() -> dict:
    cfg=_protocol("ORBIT-VALIDITY-ENVELOPE-001")
    ref=pd.read_csv(DATA/"orbital_timeseries.csv"); nbody=pd.read_csv(DATA/"orbital_timeseries_nbody_dossier.csv")
    merged=ref[["time","eccentricity","precession"]].merge(nbody[["time","eccentricity","precession"]],on="time",suffixes=("_reference","_nbody")).sort_values("time",ascending=False).reset_index(drop=True)
    times=merged["time"].to_numpy(float); ecc=(merged["eccentricity_nbody"]-merged["eccentricity_reference"]).to_numpy(float)
    prec=np.angle(np.exp(1j*(merged["precession_nbody"].to_numpy(float)-merged["precession_reference"].to_numpy(float))))
    bins=[]; age=np.abs(times)
    for lo,hi in cfg["time_bins_ka"]:
        mask=(age>=lo)&(age<hi)
        bins.append({"range_ka":[lo,hi],"n":int(mask.sum()),"eccentricity_RMSE":_r(np.sqrt(np.mean(ecc[mask]**2))),"precession_circular_RMSE_rad":_r(np.sqrt(np.mean(prec[mask]**2)))})
    oref=pd.read_csv(DATA/"orbital_reference.csv"); common=oref.merge(ref[["time","eccentricity"]],on="time",how="inner")
    error=common["eccentricity"].to_numpy(float)-common["value"].to_numpy(float); unc=common["uncertainty"].to_numpy(float); valid=unc>0; z=np.abs(error[valid])/unc[valid]
    return {"protocol_id":cfg["id"],"status":"retrospective_validation_envelope","common_nbody_points":len(merged),"eccentricity_horizons_ka":_cumulative_horizons(times,ecc,cfg["eccentricity_rmse_budgets"]),"precession_horizons_ka":_cumulative_horizons(times,prec,cfg["precession_circular_rmse_budgets_rad"]),"time_bins":bins,"uncertainty_calibration":{"reference_rows":len(common),"fraction_within_1sigma":_r(np.mean(z<=1)),"fraction_within_2sigma":_r(np.mean(z<=2)),"median_abs_z":_r(np.median(z)),"empirical_95pct_sigma_multiplier":_r(np.quantile(z,0.95)),"coverage_target_met":bool(np.mean(z<=2)>=cfg["uncertainty_calibration"]["coverage_target_at_2sigma"])},"section_XIV_credit":False}


def _climate_series(table: pd.DataFrame, model: str, scenario: str) -> tuple[pd.Series,pd.Series]:
    g=table[(table["model"]==model)&(table["scenario"]==scenario)]
    temp=g[g["variable"]=="near_surface_air_temperature_C"].groupby("time")["value"].mean().sort_index()
    nasst=g[g["variable"]=="NASST_anomaly"].groupby("time")["value"].mean().sort_index()
    temp=temp-temp.loc[1850:1900].mean(); nasst=nasst-nasst.loc[1850:1900].mean()
    return temp.rolling(11,center=True,min_periods=6).mean(), nasst.rolling(11,center=True,min_periods=6).mean()


def run_climate_matched_state() -> dict:
    cfg=_protocol("CLIMATE-MATCHED-STATE-FROZEN-001"); table=pd.read_csv(DATA/"modern_climate_ensemble.csv")
    eligible=[]
    for model,g in table.groupby("model"):
        ok=True
        for scenario in cfg["scenarios"]:
            sg=g[g["scenario"]==scenario]
            ok &= (sg["variable"]==cfg["global_state_variable"]).any() and (sg["variable"]==cfg["response_variable"]).any()
        if ok: eligible.append(model)
    levels={}
    for k,threshold in enumerate(cfg["warming_levels_C"]):
        values=[]
        for model in eligible:
            rec={}
            for scenario in cfg["scenarios"]:
                temp,nasst=_climate_series(table,model,scenario); crossing=temp[temp>=threshold]
                if len(crossing):
                    year=crossing.index[0]
                    if year in nasst.index and np.isfinite(nasst.loc[year]): rec[scenario]=float(nasst.loc[year])
            if len(rec)==2: values.append(rec[cfg["scenarios"][1]]-rec[cfg["scenarios"][0]])
        arr=np.asarray(values,float); ci=_bootstrap_mean_ci(arr,seed_offset=100+k); loo=[float(np.delete(arr,i).mean()) for i in range(len(arr))] if len(arr)>1 else []
        loo_range=[_r(min(loo)),_r(max(loo))] if loo else [None,None]
        same_sign_loo=bool(loo and ((loo_range[0]>0) or (loo_range[1]<0))); excludes=bool(ci[0]>0 or ci[1]<0)
        levels[str(threshold)]={"n_models":len(arr),"mean_effect_C":_r(arr.mean()),"median_effect_C":_r(np.median(arr)),"bootstrap95":ci,"positive_fraction":_r(np.mean(arr>0)),"leave_one_model_out_mean_range":loo_range,"robust_direction":bool(excludes and same_sign_loo)}
    signs=[np.sign(levels[str(x)]["mean_effect_C"]) for x in cfg["warming_levels_C"]]
    return {"protocol_id":cfg["id"],"status":"retrospective_calibration_frozen_for_external_reuse","eligible_models":len(eligible),"levels":levels,"adjacent_mean_sign_changes":int(sum(a!=b for a,b in zip(signs,signs[1:]))),"section_XIV_credit":False}


def run_constraint_regime() -> dict:
    cfg=_protocol("CONSTRAINT-REGIME-001"); table=pd.read_csv(DATA/"murchison_degassing_profiles.csv")
    temps=sorted(table["temperature_k"].unique()); species=sorted(table["species"].unique())
    def vector(temp,scenario):
        s=table[(table["temperature_k"]==temp)&(table["scenario"]==scenario)].set_index("species")["mole_fraction"]
        v=np.asarray([s.get(x,0.0) for x in species],float); return v/v.sum()
    contrasts=[]; within=[]
    for temp in temps:
        v=vector(temp,"vacuum"); i=vector(temp,"intermediate_oxidizing"); s=vector(temp,"strong_oxidizing")
        vi=float(jensenshannon(v,i,base=2.0)**2); vs=float(jensenshannon(v,s,base=2.0)**2); is_=float(jensenshannon(i,s,base=2.0)**2)
        contrasts.append((vi+vs)/2.0-is_); within.append(is_)
    contrast=np.asarray(contrasts,float); within=np.asarray(within,float); ci=_bootstrap_mean_ci(contrast,seed_offset=200)
    test=wilcoxon(contrast,alternative="greater")
    rule=cfg["candidate_rule"]
    candidate=bool(ci[0]>=rule["contrast_bootstrap95_lower_min_bits"] and np.mean(contrast>0)>=rule["positive_temperature_fraction_min"] and np.mean(within)<=rule["within_domain_mean_JS_max_bits"])
    return {"protocol_id":cfg["id"],"status":"retrospective_model_regime_calibration","temperatures":len(temps),"contrast_mean_bits":_r(np.mean(contrast)),"contrast_median_bits":_r(np.median(contrast)),"contrast_bootstrap95":ci,"positive_temperature_fraction":_r(np.mean(contrast>0)),"wilcoxon_greater_p":_r(test.pvalue),"within_oxidising_mean_JS_bits":_r(np.mean(within)),"regime_separation_candidate":candidate,"empirical_causal_status":False,"section_XIV_credit":False}


def compute_all_protocols() -> dict:
    results={
        "HMR-X-LADDER-001":run_hmr_x_ladder(),
        "H-DEPTH-LADDER-001":run_h_depth_ladder(),
        "PACC-VECTOR-001":run_pacc_vector(),
        "THRESHOLD-SURFACE-001":run_threshold_surface(),
        "ORBIT-VALIDITY-ENVELOPE-001":run_orbit_validity_envelope(),
        "CLIMATE-MATCHED-STATE-FROZEN-001":run_climate_matched_state(),
        "CONSTRAINT-REGIME-001":run_constraint_regime(),
    }
    return {"schema":"oric.instruments-v2-protocol-results.v1","repository_reference":"e9af333aec704707f151b2d37ab1f2576a255593","freeze_date":"2026-08-17","protocol_count":7,"results":results,"section_XIV":{"passed":7,"total":12,"unchanged":True}}


def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("--output",type=Path,default=DEFAULT_OUTPUT); args=parser.parse_args()
    result=compute_all_protocols(); args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); print(args.output); return 0

if __name__=="__main__": raise SystemExit(main())
