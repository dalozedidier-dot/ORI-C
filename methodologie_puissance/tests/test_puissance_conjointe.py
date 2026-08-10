from methodologie_puissance.puissance_conjointe_matiere import simulate
def test_power_increases_for_large_effects():
 kw=dict(strata=6,b_ht=2.0,b_tr=1.8,retention=.9,ablation_fraction=.5)
 assert simulate(120,reps=30,seed=7,**kw) >= simulate(36,reps=30,seed=7,**kw)
