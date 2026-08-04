from pathlib import Path
import importlib.util, sys
import numpy as np

MODULE = Path(__file__).resolve().parents[1] / "analyser_transfert.py"
spec = importlib.util.spec_from_file_location("transfert", MODULE)
mod = importlib.util.module_from_spec(spec); sys.modules[spec.name] = mod
assert spec.loader; spec.loader.exec_module(mod)


def test_insolation_est_finie_et_positive():
    q = mod.daily_mean_insolation(65.0, np.pi / 2, np.array([0.0167]), np.deg2rad(np.array([23.44])), np.array([1.8]))
    assert np.isfinite(q).all()
    assert (q > 0).all()


def test_ridge_reconstruit_une_relation_lineaire():
    x = np.arange(20.0)[:, None]
    y = 2.0 * x[:, 0] + 3.0
    model = mod.ridge_fit(x, y, alpha=1e-12)
    assert mod.rmse(y, mod.ridge_predict(model, x)) < 1e-6
