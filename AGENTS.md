# Repository Guidelines

- `ta_indicator.py` is the main indicator implementation that consumes the shared models defined in `base.py`.
- Prompt materials live in `docs/prompt/indicator_template.md`; `template.txt` simply points to that spec. Keep the doc updated before generating new code via AI.
- Tests live in `tests/`; shared fixtures sit under `tests/fixtures/` (e.g., `BTCUSDT-1m-2025-11.csv`). Scripts that aid generation/validation live in `scripts/`.
- Treat the repo as an extensible template by editing `ta_indicator.py` (or generating a new single-file indicator) and pairing it with regression tests.

## Build, Test, and Development Commands
- Create a virtualenv with uv: `uv venv .venv && source .venv/bin/activate`.
- Install runtime deps (numpy, pydantic, TA-Lib bindings): `uv pip install -r requirements.txt`. Install TA-Lib native libs on the host first.
- Run prompt helper: `uv run scripts/gen_indicator_prompt.py` to copy/paste the latest spec.
- Validate code before committing: `uv run scripts/validate_indicator.py` (wraps `pytest`). Use `uv run pytest -k name` for focused debugging.

## Coding Style & Naming Conventions
- Python ≥3.10, 4-space indents, full typing. Classes in `PascalCase`, functions/vars `snake_case`.
- Indicators must inherit `IndicatorBase`, accept a `BaseModel` params object, expose `on_bars(bars: List[dict])`, and return `List[IndicatorResultBase]`.
- Bar dictionaries contain `timestamp, open, high, low, close, volume` floats/ints; keep logic deterministic and side-effect free. Add concise docstrings for non-trivial sections.
- Outputs must align 1:1 with input bars; keep `nan` warmups intact. Result models live in `base.py` and are imported by `ta_indicator.py`.

## Testing Guidelines
- Use `pytest` with descriptive names (`tests/test_ta_indicator.py`). Load fixtures via helper functions to convert CSV rows into bar dicts.
- Validate timestamp alignment, value types, and boundary behaviors (empty list, short series). Cover schema errors (missing fields) as well as successful paths.
- When adding new indicators, create dedicated test modules and reuse the BTCUSDT data for deterministic regression checks.

## Automation & Workflow
- `scripts/gen_indicator_prompt.py` prints the canonical AI prompt; pipe it into an editor or API request body.
- `scripts/validate_indicator.py` wraps `pytest` to keep the validation command consistent across local dev and CI.
- Consider adding Make/CI targets that call these scripts so contributors run the exact same steps.

## Commit & Pull Request Guidelines
- Commits use short imperative subjects (e.g., “Add EMA indicator skeleton”); keep unrelated refactors separate.
- PRs must describe motivation, summarize changes, list validation commands (typically the validate script), and mention fixture/test updates. Link issues or RFCs when relevant.
- Highlight any changes to the prompt spec or shared core modules so reviewers re-run downstream generators.

## Security & Configuration Tips
- Never commit keys or credentials. Keep broker/exchange details in environment variables or `.env` ignored files.
- Document system-level dependencies (TA-Lib, uv) when adding platforms or CI targets so others can reproduce the setup quickly.
