import numpy as np

from hypnos_edge.synth import inject_artifacts, synth_ibi


def test_synth_ibi_length_and_bounds():
    ibi = synth_ibi(500, seed=0)
    assert len(ibi) == 500
    hr = 60000.0 / ibi
    assert np.all(hr >= 40.0) and np.all(hr <= 180.0)


def test_drop_shortens_array():
    ibi = synth_ibi(200, seed=1)
    out = inject_artifacts(ibi, drop_p=1.0, spurious_p=0.0, motion_p=0.0, seed=2)
    assert len(out) < 200


def test_spurious_lengthens_array():
    ibi = synth_ibi(200, seed=1)
    out = inject_artifacts(ibi, drop_p=0.0, spurious_p=1.0, motion_p=0.0, seed=2)
    assert len(out) > 200


def test_reproducible_with_same_seed():
    ibi = synth_ibi(200, seed=1)
    a = inject_artifacts(ibi, drop_p=0.1, spurious_p=0.1, motion_p=0.1, seed=42)
    b = inject_artifacts(ibi, drop_p=0.1, spurious_p=0.1, motion_p=0.1, seed=42)
    np.testing.assert_array_equal(a, b)
