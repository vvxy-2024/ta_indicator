# TA Indicator Template

Single-file technical analysis indicator scaffold featuring:
- `base.py` with shared BaseModel contracts and result objects.
- `ta_indicator.py` implementing ATR/CCI/MACD/RSI/MA/EMA via TA-Lib.
- pytest coverage using the BTCUSDT fixture under `tests/fixtures/`.

Setup (uv recommended):
```bash
uv venv .venv && source .venv/bin/activate
uv pip install -r requirements.txt
```

Prompt spec: `docs/prompt/indicator_template.md`.
