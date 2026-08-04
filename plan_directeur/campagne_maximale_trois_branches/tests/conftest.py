from __future__ import annotations

import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))


@pytest.fixture(scope="session")
def matter_result():
    from analyse_matiere import run
    return run()


@pytest.fixture(scope="session")
def solar_result():
    from analyse_systeme_solaire import run
    return run()


@pytest.fixture(scope="session")
def living_result():
    from analyse_vivant import run
    return run()
