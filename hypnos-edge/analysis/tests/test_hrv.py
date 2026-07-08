import numpy as np
import pytest

from hypnos_edge.hrv import rmssd, sdnn


def test_rmssd_by_hand(toy_ibi):
    assert rmssd(toy_ibi) == pytest.approx(15.5455, abs=1e-3)


def test_sdnn_by_hand(toy_ibi):
    assert sdnn(toy_ibi) == pytest.approx(8.5391, abs=1e-3)


def test_rmssd_needs_two_intervals():
    with pytest.raises(ValueError):
        rmssd(np.array([800.0]))


def test_sdnn_needs_two_intervals():
    with pytest.raises(ValueError):
        sdnn(np.array([]))
