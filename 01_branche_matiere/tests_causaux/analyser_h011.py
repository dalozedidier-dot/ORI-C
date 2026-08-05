from __future__ import annotations
import json
from pathlib import Path
import numpy as np, pandas as pd
ROOT=Path(__file__).resolve().parent; OUT=ROOT/'resultats'
def main():
    d=pd.read_csv(ROOT/'donnees/seuils_instabilite_streaming.csv')
    t=d[d.tau_s.eq(0.01)].sort_values('alpha_D')
    monotonic=bool(np.all(np.diff(t.z_critical)>0))
    slope=float(np.polyfit(np.log10(t.alpha_D),np.log10(t.z_critical),1)[0])
    ratio=float(t.z_critical.iloc[-1]/t.z_critical.iloc[0])
    result={'rows':len(d),'turbulence_points':len(t),'zcrit_monotonic_with_turbulence':monotonic,'log_log_slope':slope,'threshold_ratio_high_low_turbulence':ratio,'h011_status':'mechanistic_threshold_supported_in_simulations' if monotonic and ratio>=2 else 'not_supported','natural_intervention_status':'not_measured','interpretation':'H011 acquiert un seuil opératoire testable. Le résultat reste un contraste de simulations et non une ablation naturelle.'}
    OUT.mkdir(exist_ok=True); (OUT/'H011_RESULTAT.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2,ensure_ascii=False)); return result
if __name__=='__main__': main()
