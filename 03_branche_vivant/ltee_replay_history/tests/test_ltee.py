from pathlib import Path
import pandas as pd
def test_published_totals_transcribed():
 d=pd.read_csv(Path(__file__).parents[1]/'data/replay_counts_blount2008.csv')
 reps=sum(int(d[c].sum()) for c in d if c.endswith('_replicates'))
 pos=sum(int(d[c].sum()) for c in d if c.endswith('_citplus'))
 assert reps==3212 and pos==17
