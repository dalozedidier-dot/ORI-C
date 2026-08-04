#!/usr/bin/env python3
from __future__ import annotations
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
TASKS=[
 ('matiere',ROOT/'01_branche_matiere/hypergraphe_transformations/fermeture_stricte/analyser_verrou.py'),
 ('transfert_climatique',ROOT/'02_branche_systeme_solaire/transfert_climatique_intermediaire/analyser_transfert.py'),
 ('hysteresis',ROOT/'02_branche_systeme_solaire/couche_memoire_historique/stress/o_hysteresis_bassins.py'),
 ('antibiotique_externe',ROOT/'03_branche_vivant/benchmark_externe_card2019/analyser_benchmark.py'),
 ('prebiotique',ROOT/'03_branche_vivant/programme_prebiotique/auditer_donnees_reelles.py'),
]
res={}
for name,script in TASKS:
    p=subprocess.run([sys.executable,str(script)],cwd=ROOT,capture_output=True,text=True)
    res[name]={'returncode':p.returncode,'stdout_tail':p.stdout[-1200:],'stderr_tail':p.stderr[-1200:]}
    if p.returncode: print(p.stdout,p.stderr,file=sys.stderr); raise SystemExit(p.returncode)
# Load canonical verdicts
paths={
 'matiere':ROOT/'01_branche_matiere/hypergraphe_transformations/fermeture_stricte/resultats/diagnostic_fermeture.json',
 'transfert_climatique':ROOT/'02_branche_systeme_solaire/transfert_climatique_intermediaire/resultats/verdict_transfert.json',
 'hysteresis':ROOT/'02_branche_systeme_solaire/couche_memoire_historique/results_stress/hysteresis_c3/hysteresis_verdict.json',
 'antibiotique_externe':ROOT/'03_branche_vivant/benchmark_externe_card2019/resultats/verdict_externe.json',
 'prebiotique':ROOT/'03_branche_vivant/programme_prebiotique/resultats/audit_donnees_reelles.json',
}
summary={'version':'0.9.3-research','executions':res,'verdicts':{k:json.loads(v.read_text()) for k,v in paths.items()}}
(HERE/'resultats/synthese_priorites_v093.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
report='''# Campagne des priorités v0.9.3

'''
report+='- Matière : le verrou 46/53 est localisé. Une réparation candidate ferme 53/53, mais la source disponible ne démontre pas l’hyperarête exacte et la réparation reste non canonique.\n'
report+='- Astronomie vers climat : le signal N-corps apporte un gain positif dans trois fenêtres temporelles sur trois, 3,12 % en moyenne, dans une prédiction à un pas avec état climatique observé. Ce résultat ne remplace ni Terre-Lune complet, ni marées, ni GCM.\n'
report+='- Mémoire : M2 et son témoin apparié M2P présentent deux bassins. Des boucles d’hystérèse apparaissent à 30 degrés, mais aucun état matériellement différent ne subsiste après le retour complet au faible forçage.\n'
report+='- Vivant : Card 2019 fournit une réplication externe temporelle rétrospective. L’histoire linéaire est moins bonne dans chacun des quatre groupes de test et le bootstrap groupé conserve un écart défavorable.\n'
report+='- Prébiotique : deux trajectoires expérimentales de populations d’ARN catalytique sur huit cycles sont intégrées. Elles ne contiennent aucune filiation parent-descendant de compartiments, donc le critère héréditaire reste non testable.\n'
(HERE/'resultats/RAPPORT_PRIORITES_V093.md').write_text(report,encoding='utf-8')
print(json.dumps({'status':'ok','tasks':list(res)},ensure_ascii=False))
