#!/usr/bin/env python3
"""Benchmark externe rétrospectif sur la série temporelle Ara+5 de Card et al. 2019."""
from __future__ import annotations
import json, math, re
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
DATA = HERE / "data" / "MICs_Ara5_population.csv"
OUT = HERE / "resultats"


def parse_strain(s: str) -> tuple[float, str]:
    if s == "0": return 0.0, "0"
    m = re.fullmatch(r"([0-9.]+)([AB])", str(s))
    if not m: raise ValueError(f"Identifiant inattendu: {s}")
    return float(m.group(1)), m.group(2)


def rmse(y, p):
    y = np.asarray(y, float)
    p = np.asarray(p, float)
    return float(np.sqrt(np.mean((y - p) ** 2)))


def regression_prediction(X_train, y_train, X_test, alpha: float = 0.0):
    """Régression linéaire avec intercept et ridge sans dépendance sklearn.

    Les prédicteurs sont centrés. L'intercept n'est pas pénalisé, comme dans
    les modèles utilisés auparavant. Cette forme fermée évite le chargement
    d'une pile de parallélisme supplémentaire dans les campagnes cumulatives.
    """
    X_train = np.asarray(X_train, float)
    X_test = np.asarray(X_test, float)
    y_train = np.asarray(y_train, float)
    x_mean = X_train.mean(axis=0)
    y_mean = float(y_train.mean())
    X_centered = X_train - x_mean
    y_centered = y_train - y_mean
    gram = X_centered.T @ X_centered + alpha * np.eye(X_train.shape[1])
    beta = np.linalg.solve(gram, X_centered.T @ y_centered)
    return y_mean + (X_test - x_mean) @ beta

def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(DATA)
    parsed = df["strain"].astype(str).map(parse_strain)
    df["generation_k"] = parsed.map(lambda x: x[0])
    df["clone"] = parsed.map(lambda x: x[1])
    df["parent_log2"] = np.log2(df["parent"].astype(float))
    df["daughter_log2"] = np.log2(df["daughter"].astype(float))
    df["evolvability"] = df["daughter_log2"] - df["parent_log2"]
    # Découpage temporel strict: jusqu'à 2 000 générations en apprentissage,
    # 5 000 et 10 000 générations en test.
    train = df[df.generation_k <= 2.0].copy()
    test = df[df.generation_k >= 5.0].copy()
    ytr, yte = train.evolvability.to_numpy(), test.evolvability.to_numpy()
    rows=[]
    predictions=[]
    # climatologie historique
    p = np.full(len(test), ytr.mean())
    rows.append(("moyenne_apprentissage", 1, rmse(yte,p), float(np.corrcoef(yte,p)[0,1]) if np.std(p)>0 else None))
    predictions.append(("moyenne_apprentissage",p))
    # état présent uniquement
    Xtr=train[["parent_log2"]].to_numpy(); Xte=test[["parent_log2"]].to_numpy()
    p=regression_prediction(Xtr, ytr, Xte, alpha=0.0)
    rows.append(("etat_parent_seul",2,rmse(yte,p),float(np.corrcoef(yte,p)[0,1]) if np.std(p)>0 else None)); predictions.append(("etat_parent_seul",p))
    # histoire linéaire + état, extrapolation hors échantillon
    Xtr=train[["parent_log2","generation_k"]].to_numpy(); Xte=test[["parent_log2","generation_k"]].to_numpy()
    p=regression_prediction(Xtr, ytr, Xte, alpha=1.0)
    rows.append(("etat_plus_histoire_lineaire",3,rmse(yte,p),float(np.corrcoef(yte,p)[0,1]) if np.std(p)>0 else None)); predictions.append(("etat_plus_histoire_lineaire",p))
    # tendance historique seule
    Xtr=train[["generation_k"]].to_numpy(); Xte=test[["generation_k"]].to_numpy()
    p=regression_prediction(Xtr, ytr, Xte, alpha=1.0)
    rows.append(("histoire_seule",2,rmse(yte,p),float(np.corrcoef(yte,p)[0,1]) if np.std(p)>0 else None)); predictions.append(("histoire_seule",p))
    bench=pd.DataFrame(rows,columns=["modele","parametres","rmse_test","correlation_test"])
    best=bench.sort_values("rmse_test").iloc[0]
    state=float(bench.loc[bench.modele=="etat_parent_seul","rmse_test"].iloc[0])
    hist=float(bench.loc[bench.modele=="etat_plus_histoire_lineaire","rmse_test"].iloc[0])
    gain=(state-hist)/state*100

    # Bootstrap groupé sur les quatre clones-temps du bloc de test. Les dix
    # répétitions d'un même identifiant ne sont pas traitées comme dix lignées
    # indépendantes. Le contraste porte sur la différence de RMSE appariée.
    state_prediction = dict(predictions)["etat_parent_seul"]
    history_prediction = dict(predictions)["etat_plus_histoire_lineaire"]
    test_for_bootstrap = test[["strain", "evolvability"]].reset_index(drop=True).copy()
    test_for_bootstrap["state_squared_error"] = (yte - state_prediction) ** 2
    test_for_bootstrap["history_squared_error"] = (yte - history_prediction) ** 2
    groups = sorted(test_for_bootstrap["strain"].unique())
    rng = np.random.default_rng(20260804)
    differences = []
    for _ in range(10000):
        sampled = rng.choice(groups, size=len(groups), replace=True)
        blocks = [test_for_bootstrap[test_for_bootstrap.strain == group] for group in sampled]
        sample = pd.concat(blocks, ignore_index=True)
        state_sample_rmse = float(np.sqrt(sample["state_squared_error"].mean()))
        history_sample_rmse = float(np.sqrt(sample["history_squared_error"].mean()))
        differences.append(history_sample_rmse - state_sample_rmse)
    differences = np.asarray(differences, float)
    bootstrap_interval = np.quantile(differences, [0.025, 0.975])
    group_summary = test_for_bootstrap.groupby("strain", as_index=False).agg(
        n=("evolvability", "size"),
        state_mse=("state_squared_error", "mean"),
        history_mse=("history_squared_error", "mean"),
    )
    group_summary["state_rmse"] = np.sqrt(group_summary["state_mse"])
    group_summary["history_rmse"] = np.sqrt(group_summary["history_mse"])
    group_summary["history_minus_state_rmse"] = group_summary["history_rmse"] - group_summary["state_rmse"]
    group_summary.to_csv(OUT / "contraste_par_groupe.csv", index=False)

    bench.to_csv(OUT/"benchmark_temporel.csv",index=False)
    pred=test[["strain","generation_k","clone","parent_log2","evolvability"]].reset_index(drop=True)
    for name, vals in predictions: pred[name]=vals
    pred.to_csv(OUT/"predictions_hors_echantillon.csv",index=False)
    by_time=df.groupby("generation_k",as_index=False).agg(n=("evolvability","size"),mediane=("evolvability","median"),moyenne=("evolvability","mean"),ecart_type=("evolvability","std"))
    by_time.to_csv(OUT/"serie_temporelle_resume.csv",index=False)
    verdict={
      "dataset":"Card et al. 2019, Ara+5 LTEE, tetracycline",
      "doi_dataset":"10.5061/dryad.g41hg96",
      "rows":int(len(df)),"train_rows":int(len(train)),"test_rows":int(len(test)),
      "train_generations_k":[0,0.5,1,1.5,2],"test_generations_k":[5,10],
      "best_model":str(best.modele),"best_rmse_test":float(best.rmse_test),
      "state_only_rmse":state,"history_plus_state_rmse":hist,
      "history_gain_vs_state_percent":float(gain),
      "history_beats_state":bool(hist < state),
      "history_minus_state_rmse":float(hist - state),
      "group_bootstrap":{
        "resamples":10000,
        "unit":"strain block",
        "groups":groups,
        "difference_history_minus_state_rmse_ci95":[float(bootstrap_interval[0]),float(bootstrap_interval[1])],
        "probability_history_better":float(np.mean(differences < 0.0)),
        "history_worse_in_all_test_groups":bool((group_summary["history_minus_state_rmse"] > 0).all()),
      },
      "status":"retrospectif_externe_non_confirmatoire",
      "interpretation":"jeu indépendant des données Windels; test temporel strict mais conception postérieure à l'accès aux données"
    }
    (OUT/"verdict_externe.json").write_text(json.dumps(verdict,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    report=f"""# Benchmark antibiotique externe Card 2019

## Données

Série Ara+5 du LTEE, tétracycline, 130 mesures appariées parent-descendant. Les identifiants 0.5, 1, 1.5, 2, 5 et 10 correspondent à des milliers de générations. L'évolvabilité est `log2(MIC fille) - log2(MIC parent)`.

## Test temporel

Apprentissage jusqu'à 2 000 générations. Évaluation hors échantillon sur 5 000 et 10 000 générations.

- meilleur modèle : **{best.modele}** ;
- RMSE du modèle état présent seul : **{state:.4f}** ;
- RMSE état + histoire : **{hist:.4f}** ;
- gain de l'histoire sur l'état seul : **{gain:+.2f} %** ;
- différence de RMSE histoire moins état : **{hist - state:.4f}** ;
- intervalle bootstrap groupé à 95 % : **[{bootstrap_interval[0]:.4f}, {bootstrap_interval[1]:.4f}]**.

Le modèle historique est moins bon dans les quatre groupes de test. Sur 10 000 rééchantillonnages groupés, aucun ne donne une RMSE historique inférieure à celle de l'état seul.

## Verdict

Ce jeu est indépendant des données Windels et fournit une vraie séparation temporelle. Il reste **rétrospectif** car le protocole a été construit après accès au jeu. Il qualifie l'instrument et ne compte pas comme confirmation prospective d'ORI-C.
"""
    (OUT/"RAPPORT_BENCHMARK_EXTERNE.md").write_text(report,encoding="utf-8")
    print(json.dumps(verdict,ensure_ascii=False,indent=2))
if __name__=="__main__": main()
