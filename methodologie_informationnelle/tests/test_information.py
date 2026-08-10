import numpy as np
from methodologie_informationnelle.pid import pid_imin
from methodologie_informationnelle.causal_states import reconstruct

def test_pid_xor_synergy():
    x=[0,0,1,1]*50; m=[0,1,0,1]*50; y=[a^b for a,b in zip(x,m)]
    r=pid_imin(x,m,y)
    assert r['synergy_XM_bits'] > 0.99
    assert abs(r['unique_M_history_bits']) < 1e-12

def test_causal_state_periodic_vs_noise():
    periodic=np.tile([0.,1.,2.,3.],100)
    r=reconstruct(periodic,n_symbols=4,history_length=2,js_threshold=0.03,min_history_count=2)
    assert r['n_states'] >= 2
    assert r['E_finite_bits'] > 0.5
