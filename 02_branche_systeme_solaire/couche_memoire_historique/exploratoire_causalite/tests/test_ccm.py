from pathlib import Path
from importlib.util import spec_from_file_location,module_from_spec
import numpy as np
P=Path(__file__).parents[1]/'ccm.py';s=spec_from_file_location('ccm',P);m=module_from_spec(s);s.loader.exec_module(m)
def test_ccm_runs_and_is_bounded():
 t=np.linspace(0,30,600); x=np.sin(t); y=x*x+.1*np.sin(3*t)
 r=m.skill(x,y,300,E=3,tau=2,repeats=3,seed=1)
 assert -1 <= r['mean_rho'] <= 1
