import numpy as np
import pytest


@pytest.fixture
def toy_ibi() -> np.ndarray:
    return np.array([800.0, 810.0, 790.0, 805.0])
