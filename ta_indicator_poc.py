"""Volume Profile indicator computing running POC/VAH/VAL."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List, Tuple, Union

import math

from pydantic import BaseModel, Field, validator

from base import IndicatorBase, IndicatorResultBase


class POCResult(IndicatorResultBase):
    poc: float | None = Field(default=None, description="Point of Control price level")
    vah: float | None = Field(default=None, description="Value Area High (covering 70% volume)")
    val: float | None = Field(default=None, description="Value Area Low (covering 70% volume)")


class POCParams(BaseModel):
    value_area_pct: float = Field(0.7, ge=0.0, le=1.0, description="Value-area coverage ratio")

    @validator("value_area_pct")
    def _non_zero(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("value_area_pct must be greater than 0")
        return v


class ta_indicator_poc(IndicatorBase):
    """Compute POC/VAH/VAL metrics cumulatively from the first bar onward."""

    VERSION = "1.0.0"

    def __init__(self, params: Union[POCParams, Dict[str, Any], None] = None):
        """
        Accepts either a POCParams instance or a dict with `value_area_pct`.
        Defaults to 70% coverage when params omitted.
        """
        if params is None:
            self.params = POCParams()
        else:
            self.params = params if isinstance(params, POCParams) else POCParams(**params)

    def describe_purpose(self) -> str:
        return (
            "Accumulate all bars from the start of the dataset to build a running volume profile. "
            "At each bar, output the Point of Control (highest-volume price) plus the value-area "
            "high/low bounds covering the configured percentage of total volume."
        )

    def describe_params(self) -> str:
        return (
            "POCParams or dict with `value_area_pct` (float 0-1, default 0.7) "
            "specifying how much of the cumulative volume must be included in the value area."
        )

    def describe_output(self) -> str:
        return (
            "Returns a list of POCResult objects (timestamp-aligned). For each bar, POC/VAH/VAL "
            "reflect the running profile from the first bar through the current bar."
        )

    def on_bar(self, bars: List[list]) -> List[IndicatorResultBase]:
        if not bars:
            return []

        parsed_rows = self._parse_bars(bars)
        profile = defaultdict(float)
        results: List[POCResult] = []

        for timestamp, close_price, volume in parsed_rows:
            profile[close_price] += volume
            poc, vah, val = self._compute_profile(profile)
            results.append(
                POCResult(
                    timestamp=timestamp,
                    poc=poc,
                    vah=vah,
                    val=val,
                )
            )

        return results

    @staticmethod
    def _parse_bars(bars: List[list]) -> List[Tuple[int, float, float]]:
        parsed = []
        for row in bars:
            if not isinstance(row, (list, tuple)) or len(row) < 7:
                raise ValueError(
                    "Each bar must be a list like [timestamp, open, high, low, close, volume, is_close]"
                )
            timestamp = int(row[0])
            close = float(row[4])
            volume = float(row[5])
            parsed.append((timestamp, close, volume))
        return parsed

    def _compute_profile(self, profile: Dict[float, float]) -> Tuple[float | None, float | None, float | None]:
        if not profile:
            return None, None, None

        total_volume = sum(profile.values())
        if total_volume <= 0:
            return None, None, None

        sorted_levels = sorted(profile.items(), key=lambda item: (-item[1], item[0]))
        poc_price, poc_volume = sorted_levels[0]

        target_volume = total_volume * self.params.value_area_pct
        accum_volume = poc_volume
        included_prices = {poc_price}

        remaining = sorted_levels[1:]
        for price, vol in remaining:
            if accum_volume >= target_volume:
                break
            included_prices.add(price)
            accum_volume += vol

        vah = max(included_prices) if included_prices else None
        val = min(included_prices) if included_prices else None

        return (
            ta_indicator_poc._clean(poc_price),
            ta_indicator_poc._clean(vah),
            ta_indicator_poc._clean(val),
        )

    @staticmethod
    def _clean(value: float | None) -> float | None:
        if value is None:
            return None
        return value if not math.isnan(value) else None
