from importlib.util import spec_from_file_location,module_from_spec
from pathlib import Path
P=Path(__file__).with_name('topologie_persistante.py'); s=spec_from_file_location('tp',P);m=module_from_spec(s);s.loader.exec_module(m)
def test_triangle_cycle_dies_when_face_arrives():
 f={('a',):0,('b',):0,('c',):0,('a','b'):0.2,('a','c'):0.2,('b','c'):0.2,('a','b','c'):0.7}
 _,ints=m.persistence(f); h1=[x for x in ints if x['dimension']==1]
 assert any(abs(x['birth']-.2)<1e-12 and abs(x['death']-.7)<1e-12 for x in h1)
