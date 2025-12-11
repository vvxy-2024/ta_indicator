# Indicator Prompt Specification

Use this specification when requesting a new indicator class from an AI model. It mirrors the expectations enforced by `ta_indicator.py` (which consumes `base.py`) and the pytest harness.

## 1. Required Structure
1. Indicator classes inherit `IndicatorBase` from `base.py`.
2. Initialization accepts a single `BaseModel` parameters object (e.g., `MACDParams`).
3. Indicators implement `on_bars(self, bars: List[list]) -> List[IndicatorResultBase]` and support `with` context management.

## 2. Input Schema
- `bars` is a list of lists in the order `[timestamp, open, high, low, close, volume, is_close]`.
- The method must accept the full series and preserve order.

## 3. Output Schema
- Every result inherits `IndicatorResultBase`:
  ```python
  class IndicatorResultBase(BaseModel):
      timestamp: int = Field(..., description="K线时间戳")
  ```
- For MACD-style indicators, extend with typed fields:
  ```python
  class MACDResult(IndicatorResultBase):
      macd: float = Field(..., description="MACD值")
      signal: float = Field(..., description="信号线")
      hist: float = Field(..., description="柱状图")
  ```
- The output list length equals input bars length; preserve timestamps even if values are `nan`.

## 4. Implementation Checklist
1. Extract timestamps and price arrays (`open/high/low/close/volume`).
2. Call TA-Lib (preferred) or an equivalent numeric library.
3. Convert indicator arrays to result instances aligned with timestamps.
4. Return the full list without truncation; keep `nan` for warm-up periods.
5. Document parameters via `BaseModel` with `Field` descriptions.

## 5. Example Prompt Block
````markdown
You are generating a production-ready indicator class.

- Subclass `IndicatorBase`; params use `BaseModel`.
- Implement `on_bars(bars: List[dict]) -> List[IndicatorResultBase]`.
- Use TA-Lib for calculations; maintain full-length outputs and timestamp alignment.
- Define result models inheriting `IndicatorResultBase`. Example for MACD shown below.
- Support `with` context usage and keep logic deterministic.

Example scaffold:
```python
class MACDParams(BaseModel):
    fastperiod: int = Field(12, ge=1)
    slowperiod: int = Field(26, ge=1)
    signalperiod: int = Field(9, ge=1)

class MACDIndicator(IndicatorBase):
    def on_bars(self, bars: List[dict]) -> List[MACDResult]:
        closes = np.array([bar["close"] for bar in bars], dtype=float)
        timestamps = [bar["timestamp"] for bar in bars]
        macd, signal, hist = talib.MACD(...)
        return [
            MACDResult(timestamp=ts, macd=float(m), signal=float(s), hist=float(h))
            for ts, m, s, h in zip(timestamps, macd, signal, hist)
        ]
```
````

## 6. Usage Notes
- Keep indicator implementations in `ta_indicator.py` (or another single-file module) so they remain easy to drop into downstream systems.
- Add your own regression tests (pytest recommended) using the BTCUSDT fixture if automated validation is desired.
- Run any validation scripts or linting tools you add before submitting PRs.
