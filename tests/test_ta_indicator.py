import csv
import math
from pathlib import Path

import pytest

from ta_indicator import (
    ATRResult,
    CCIResult,
    EMAResult,
    MAResult,
    MACDResult,
    RSIResult,
    TAConfig,
    ta_indicator,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "BTCUSDT-1m-2025-11.csv"


def _load_bars(limit: int = 300):
    bars = []
    with FIXTURE_PATH.open("r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            bars.append(
                {
                    "timestamp": int(row["open_time"]),
                    "open": float(row["open"]),
                    "high": float(row["high"]),
                    "low": float(row["low"]),
                    "close": float(row["close"]),
                    "volume": float(row["volume"]),
                }
            )
            if len(bars) >= limit:
                break
    return bars


@pytest.fixture(scope="module")
def bars():
    loaded = _load_bars()
    assert loaded, "Fixture CSV should provide bar data"
    return loaded


@pytest.mark.parametrize(
    ("name", "params", "result_cls", "fields"),
    [
        ("ATR", (14,), ATRResult, ("atr",)),
        ("CCI", (20,), CCIResult, ("cci",)),
        ("MACD", (12, 26, 9), MACDResult, ("macd", "signal", "hist")),
        ("RSI", (14,), RSIResult, ("rsi",)),
        ("MA", (20,), MAResult, ("ma",)),
        ("EMA", (20,), EMAResult, ("ema",)),
    ],
)
def test_indicator_outputs_align_with_bars(bars, name, params, result_cls, fields):
    cfg = TAConfig(name=name, params=params)
    with ta_indicator(cfg) as indicator:
        results = indicator.on_bar(bars)

    assert len(results) == len(bars)
    assert all(isinstance(res, result_cls) for res in results)

    for res, bar in zip(results, bars):
        assert res.timestamp == bar["timestamp"]
        for field in fields:
            value = getattr(res, field)
            assert value is None or isinstance(value, float)
            if isinstance(value, float) and not math.isnan(value):
                # ensure reasonable numeric magnitude
                assert abs(value) < 1e9


def test_on_bar_requires_all_fields():
    cfg = TAConfig(name="ATR", params=(14,))
    bad_bars = [{"timestamp": 1, "open": 1.0, "high": 1.0, "low": 1.0, "close": 1.0}]
    with ta_indicator(cfg) as indicator:
        with pytest.raises(ValueError):
            indicator.on_bar(bad_bars)
