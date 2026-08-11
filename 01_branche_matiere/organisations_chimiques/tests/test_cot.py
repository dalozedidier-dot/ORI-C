from importlib.util import spec_from_file_location,module_from_spec
from pathlib import Path
P=Path(__file__).parents[1]/'cot.py'; s=spec_from_file_location('cot',P);m=module_from_spec(s);s.loader.exec_module(m)
def test_cycle_is_organization():
 rs=[{'reactants':['A'],'products':['B'],'stoich':{'A':-1,'B':1}}, {'reactants':['B'],'products':['A'],'stoich':{'B':-1,'A':1}}]
 assert m.is_organization({'A','B'},rs)
def test_open_set_not_closed():
 rs=[{'reactants':['A'],'products':['B'],'stoich':{'A':-1,'B':1}}]
 assert not m.is_closed({'A'},rs)
