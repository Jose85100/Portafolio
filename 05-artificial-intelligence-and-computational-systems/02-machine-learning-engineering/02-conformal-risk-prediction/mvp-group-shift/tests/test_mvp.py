import numpy as np
import pytest
from src.quantile import radius
from src.case import case
from src.benchmark import run

def test_order_statistic():
    assert radius(np.arange(1., 11.)) == 10.

def test_small_sample():
    assert np.isinf(radius([1., 2.]))

@pytest.mark.parametrize("bad", [[], [-1.], [np.nan]])
def test_invalid(bad):
    with pytest.raises(ValueError):
        radius(bad)

def test_reproducible():
    a = case(7, "mixture_shift")
    b = case(7, "mixture_shift")
    assert np.array_equal(a[0], b[0])

def test_benchmark(tmp_path):
    rows = run(tmp_path/"raw.csv")
    assert len(rows) == 240
    assert (tmp_path/"raw.csv").exists()
