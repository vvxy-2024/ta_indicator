"""Shared base classes and result models for indicators."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from pydantic import BaseModel, Field


class IndicatorResultBase(BaseModel):
    """Base result object; every indicator result must include timestamp."""

    timestamp: int = Field(..., description="K线时间戳")
    buy: Optional[bool] = Field(default=None, description="buy signal")
    sell: Optional[bool] = Field(default=None, description="sell signal")


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


class IndicatorBase(ABC):
    """Base context-managed indicator."""

    VERSION = "1.0.0"

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    @abstractmethod
    def describe_purpose(self) -> str:
        """Return a human-readable description of what the indicator does."""

    @abstractmethod
    def describe_params(self) -> str:
        """Return detailed information about expected initialization parameters."""

    @abstractmethod
    def describe_output(self) -> str:
        """Return detailed information about the output structure."""

    @abstractmethod
    def on_bar(self, bars: List[dict]) -> List[IndicatorResultBase]:
        raise NotImplementedError
