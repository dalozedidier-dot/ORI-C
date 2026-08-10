#!/usr/bin/env python3
from __future__ import annotations
import json,sys
from pathlib import Path
import numpy as np, pandas as pd
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
from run_spin_orbit import load_earth, load_la2004, build_spin_frame, INTERVENTIONS
from spin_orbit import integrate_spin_batch, ALPHA_WITH_MOON_ARCSEC_PER_YEAR, daily_mean_insolation
OUT=HERE/'resultats/viabilite'; OUT.mkdir(parents=True,exist_ok=True)

def bounds_from_reference():
    baseline=pd.read_csv(HERE/'resultats/baseline_with_moon_20myr.csv')
    baseline=baseline[baseline.elapsed_years<=2_000_000]
    ref=load_la2004(2_000_000)
    eps_ref=np.degrees(ref.obliquity_rad.to_numpy())
    q_ref=daily_mean_insolation(ref.eccentricity.to_numpy(),ref.long_peri_moving_rad.to_numpy(),eps_ref)
    eps=np.r_[baseline.obliquity_deg.to_numpy(),eps_ref]
    q=np.r_[baseline.insolation_65n_solstice_w_m2.to_numpy(),q_ref]
    return {'obliquity_deg':[float(eps.min()),float(eps.max())], 'insolation_w_m2':[float(q.min()),float(q.max())]}

def metrics(job,frame,b):
    eps=frame.obliquity_deg.to_numpy(); q=frame.insolation_65n_solstice_w_m2.to_numpy()
    elo,ehi=b['obliquity_deg']; qlo,qhi=b['insolation_w_m2']
    inside=(eps>=elo)&(eps<=ehi)&(q>=qlo)&(q<=qhi)
    escale=ehi-elo; qscale=qhi-qlo
    de=np.maximum(np.maximum(elo-eps,eps-ehi),0)/escale
    dq=np.maximum(np.maximum(qlo-q,q-qhi),0)/qscale
    dn=np.sqrt(de*de+dq*dq)
    idx=np.flatnonzero(~inside)
    return {'job':job,'samples':len(frame),'fraction_inside_reference_envelope':float(inside.mean()),
            'fraction_outside_reference_envelope':float((~inside).mean()),
            'first_exit_elapsed_years':None if len(idx)==0 else float(frame.elapsed_years.iloc[idx[0]]),
            'max_normalized_boundary_excursion':float(dn.max()),
            'mean_normalized_boundary_excursion':float(dn.mean()),
            'obliquity_min_deg':float(eps.min()),'obliquity_max_deg':float(eps.max()),
            'insolation_min_w_m2':float(q.min()),'insolation_max_w_m2':float(q.max())}

def main():
    b=bounds_from_reference()
    jobs=['baseline_20myr_dt10',*INTERVENTIONS]
    orbits=[load_earth(j,2_000_000) for j in jobs]
    obl,spins,normals=integrate_spin_batch(orbits,ALPHA_WITH_MOON_ARCSEC_PER_YEAR,substeps_per_orbital_sample=10)
    frames=[build_spin_frame(o,obl[i],spins[i],normals[i]) for i,o in enumerate(orbits)]
    rows=[metrics(j,f,b) for j,f in zip(jobs,frames)]
    pd.DataFrame(rows).to_csv(OUT/'trajectoires_frontiere.csv',index=False)
    inter=rows[1:]
    result={'schema':'oric.viability-bridge.v1','status':'trajectory_viability_executed_kernel_not_estimated',
      'formalism':'Viability-theory bridge: constraint set K and trajectory distance to its boundary.',
      'constraint_set_K':{'construction':'union envelope of La2004 and ORI-C baseline-with-effective-Moon over 0-2 Myr; descriptive reference envelope, not a habitability threshold',**b},
      'kernel_status':'not_estimated_no_time_local_control_set','capture_basin_status':'not_estimated_no_time_local_control_set',
      'reason':'The six architectural interventions are fixed counterfactual architectures, not a time-local admissible control family u(t); claiming a viability kernel would overstate the available model.',
      'baseline':rows[0],'interventions':inter,
      'interventions_exiting_reference_envelope':sum(r['fraction_outside_reference_envelope']>0 for r in inter),
      'interventions_total':len(inter),
      'Pacc_frontier_exit_fraction_descriptive':sum(r['fraction_outside_reference_envelope']>0 for r in inter)/len(inter),
      'warning':'Pacc_frontier_exit_fraction_descriptive is a finite intervention-set statistic, not a probability measure over all accessible futures.'}
    (OUT/'RESULTAT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (OUT/'RAPPORT.md').write_text('# Pont avec la théorie de la viabilité\n\nLe calcul mesure la position des trajectoires par rapport à une enveloppe de référence dérivée de La2004 et du témoin ORI-C. Il **ne prétend pas calculer un noyau de viabilité**, car le modèle ne fournit pas encore un ensemble de contrôles locaux admissibles `u(t)`.\n\nToutes les métriques détaillées sont dans `RESULTAT.json` et `trajectoires_frontiere.csv`.\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
