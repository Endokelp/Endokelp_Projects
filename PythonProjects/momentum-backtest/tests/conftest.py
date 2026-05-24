import pandas as pd
import pytest


@pytest.fixture
def toy_prices_3x6() -> pd.DataFrame:
    """
    3 assets × 6 monthly periods.

    A trends up, B trends down, C is flat.

    Hand-computed expectations (lookback=2, skip=1):
      Signal at index 3 = prices[2] / prices[0] - 1
        A: 120/100 - 1 =  0.20
        B:  80/100 - 1 = -0.20
        C: 100/100 - 1 =  0.00
      Ranking: A > C > B  →  top-1 = A

      Return at index 4 (A holds):  140/130 - 1 ≈ 0.076923
      Signal at index 4 = prices[3] / prices[1] - 1
        A: 130/110 - 1 ≈  0.181818
        B:  70/ 90 - 1 ≈ -0.222222
        C: 100/100 - 1 =  0.000000
      Return at index 5 (A still holds): 150/140 - 1 ≈ 0.071429
    """
    data = {
        "A": [100.0, 110.0, 120.0, 130.0, 140.0, 150.0],
        "B": [100.0,  90.0,  80.0,  70.0,  60.0,  50.0],
        "C": [100.0, 100.0, 100.0, 100.0, 100.0, 100.0],
    }
    return pd.DataFrame(data, index=pd.date_range("2020-01-31", periods=6, freq="ME"))


@pytest.fixture
def reversal_prices() -> pd.DataFrame:
    """
    3 assets designed to expose lookahead effects.

    A: steady uptrend then crash at t=4
    B: steady downtrend then spike at t=4
    C: flat

    Hand-computed expectations (lookback=3, skip=1 vs skip=0):

      CORRECT (skip=1) signal at t=4: uses prices[3] / prices[0] - 1
        A: 115/100 - 1 =  0.150   ← WINNER
        B:  85/100 - 1 = -0.150   ← LOSER

      LOOKAHEAD (skip=0) signal at t=4: uses prices[4] / prices[1] - 1
        A:  50/105 - 1 ≈ -0.5238  ← LOSER  (rankings inverted!)
        B: 200/ 95 - 1 ≈  1.1053  ← WINNER
    """
    data = {
        "A": [100.0, 105.0, 110.0, 115.0,  50.0,  55.0],
        "B": [100.0,  95.0,  90.0,  85.0, 200.0, 180.0],
        "C": [100.0, 100.0, 100.0, 100.0, 100.0, 100.0],
    }
    return pd.DataFrame(data, index=pd.date_range("2020-01-31", periods=6, freq="ME"))
