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
