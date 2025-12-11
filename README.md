# TA Indicator Template

Single-file technical analysis indicator scaffold featuring:
- `base.py` with shared BaseModel contracts and result objects.
- `ta_indicator.py` implementing ATR/CCI/MACD/RSI/MA/EMA via TA-Lib.
- `ta_indicator_poc.py` delivering a per-day volume profile (POC/VAH/VAL) indicator.
- BTCUSDT bar sample (`BTCUSDT-1m-2025-11.csv`) for manual or custom testing.

Setup (uv recommended):
```bash
uv venv .venv && source .venv/bin/activate
uv pip install -r requirements.txt
```

Prompt spec: `docs/prompt/indicator_template.md`.
