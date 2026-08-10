from comparaisons_externes.assembly_theory.bridge import assembly_ensemble_score
def test_zero_for_single_copies(): assert assembly_ensemble_score([1,2,3],[1,1,1])==0.0
def test_positive_for_repeated_complex_objects(): assert assembly_ensemble_score([1,3],[1,4])>0
