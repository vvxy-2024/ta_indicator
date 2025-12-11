"""Single-file indicator implementation for ATR/CCI/MACD/RSI/MA/EMA."""

from __future__ import annotations

import math
from typing import Dict, List, Tuple

import numpy as np
import talib
from pydantic import BaseModel, Field, validator

from base import (
    IndicatorBase,
    IndicatorResultBase,
)

class MACDResult(IndicatorResultBase):
    macd: float = Field(..., description="MACD值")
    signal: float = Field(..., description="信号线")
    hist: float = Field(..., description="柱状图")


class ATRResult(IndicatorResultBase):
    atr: float = Field(..., description="ATR值")


class CCIResult(IndicatorResultBase):
    cci: float = Field(..., description="CCI值")


class RSIResult(IndicatorResultBase):
    rsi: float = Field(..., description="RSI值")


class MAResult(IndicatorResultBase):
    ma: float = Field(..., description="MA值")


class EMAResult(IndicatorResultBase):
    ema: float = Field(..., description="EMA值")


class TAConfig(BaseModel):
    """
    Configuration for a single indicator computation.
    Examples:
        TAConfig(name="MACD", params=(12, 26, 9))
        TAConfig(name="ATR", params=(14,))
    """

    name: str = Field(..., description="指标名称：ATR/CCI/MACD/RSI/MA/EMA")
    params: Tuple[float, ...] = Field(default_factory=tuple, description="指标参数")

    @validator("name")
    def _name_upper(cls, value: str) -> str:
        supported = {"ATR", "CCI", "MACD", "RSI", "MA", "EMA"}
        upper = value.upper()
        if upper not in supported:
            raise ValueError(f"Unsupported indicator {value}, must be one of {sorted(supported)}")
        return upper

class ta_indicator(IndicatorBase):
    """Compute a single indicator (ATR, CCI, MACD, RSI, MA, or EMA) for bar data."""

    VERSION = "1.0.0"

    _DEFAULT_PARAMS: Dict[str, Tuple[float, ...]] = {
        "ATR": (14,),
        "CCI": (20,),
        "MACD": (12, 26, 9),
        "RSI": (14,),
        "MA": (20,),
        "EMA": (20,),
    }

    def __init__(self, params: TAConfig):
        self.params = params

    def describe_purpose(self) -> str:
        return (
            "Compute a TA-Lib indicator (ATR/CCI/MACD/RSI/MA/EMA) based on the configured name "
            "and align results with the provided bar timestamps."
        )

    def describe_params(self) -> str:
        return (
            "TAConfig(name: str, params: Tuple[float, ...]). "
            "name selects the TA-Lib function (ATR/CCI/MACD/RSI/MA/EMA). "
            "params supplies the periods: ATR(timeperiod), CCI(timeperiod), "
            "MACD(fast, slow, signal), RSI(timeperiod), MA(timeperiod), EMA(timeperiod). "
            "If params is empty the class defaults to (14), (20), or (12,26,9) accordingly."
        )

    def describe_output(self) -> str:
        return (
            "Returns List[IndicatorResultBase] aligned with input bars. "
            "Each entry contains the original timestamp plus indicator-specific fields "
            "(atr/cci/rsi/ma/ema or macd/signal/hist). Warm-up elements may be NaN."
        )

    def on_bar(self, bars: List[dict]) -> List[IndicatorResultBase]:
        if not bars:
            return []

        required_keys = {"timestamp", "open", "high", "low", "close", "volume"}
        if any(not required_keys.issubset(bar) for bar in bars):
            raise ValueError(f"Each bar must include keys: {sorted(required_keys)}")

        closes = np.array([bar["close"] for bar in bars], dtype=float)
        highs = np.array([bar["high"] for bar in bars], dtype=float)
        lows = np.array([bar["low"] for bar in bars], dtype=float)
        timestamps = [bar["timestamp"] for bar in bars]

        name = self.params.name  # already upper-cased by validator
        args = self.params.params or self._DEFAULT_PARAMS[name]

        if name == "ATR":
            (period,) = args
            values = talib.ATR(highs, lows, closes, timeperiod=int(period))
            return self._build_results(timestamps, values, ATRResult, field="atr")

        if name == "CCI":
            (period,) = args
            values = talib.CCI(highs, lows, closes, timeperiod=int(period))
            return self._build_results(timestamps, values, CCIResult, field="cci")

        if name == "MACD":
            fast, slow, signal = args
            macd, signal_arr, hist = talib.MACD(
                closes,
                fastperiod=int(fast),
                slowperiod=int(slow),
                signalperiod=int(signal),
            )
            return [
                MACDResult(
                    timestamp=ts,
                    macd=self._clean_value(macd[idx]),
                    signal=self._clean_value(signal_arr[idx]),
                    hist=self._clean_value(hist[idx]),
                )
                for idx, ts in enumerate(timestamps)
            ]

        if name == "RSI":
            (period,) = args
            values = talib.RSI(closes, timeperiod=int(period))
            return self._build_results(timestamps, values, RSIResult, field="rsi")

        if name == "MA":
            (period,) = args
            values = talib.SMA(closes, timeperiod=int(period))
            return self._build_results(timestamps, values, MAResult, field="ma")

        if name == "EMA":
            (period,) = args
            values = talib.EMA(closes, timeperiod=int(period))
            return self._build_results(timestamps, values, EMAResult, field="ema")

        raise ValueError(f"Unsupported indicator: {name}")

    @staticmethod
    def _clean_value(value: float) -> float:
        return value if not math.isnan(value) else math.nan

    def _build_results(
        self,
        timestamps: List[int],
        values: np.ndarray,
        model: type,
        field: str,
    ) -> List[IndicatorResultBase]:
        results: List[IndicatorResultBase] = []
        for idx, ts in enumerate(timestamps):
            payload = {
                "timestamp": ts,
                field: self._clean_value(values[idx]),
            }
            results.append(model(**payload))
        return results
