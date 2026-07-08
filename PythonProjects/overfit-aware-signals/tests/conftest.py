import pandas as pd
import pytest


@pytest.fixture
def toy_prices_3x6() -> pd.DataFrame:
    # 3 assets x 6 monthly periods: A trends up, B trends down, C flat.
    data = {
        "A": [100.0, 110.0, 120.0, 130.0, 140.0, 150.0],
        "B": [100.0, 90.0, 80.0, 70.0, 60.0, 50.0],
        "C": [100.0, 100.0, 100.0, 100.0, 100.0, 100.0],
    }
    return pd.DataFrame(data, index=pd.date_range("2020-01-31", periods=6, freq="ME"))
