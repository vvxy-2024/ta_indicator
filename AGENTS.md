# Repository Guidelines

- `ta_indicator.py` and `ta_indicator_poc.py` provide ready-made indicators (multi-TA and daily volume profile). Both consume the shared contracts in `base.py`.
- Prompt materials live in `docs/prompt/indicator_template.md`; `template.txt` simply points to that spec. Keep the doc updated before generating new code via AI.
- Scripts or helper utilities should live under `scripts/` (add as needed). Historical fixtures/tests were removed to keep the template lightweight; add your own when required.
- Treat the repo as an extensible template by editing `ta_indicator.py` (or generating a new single-file indicator) and, if needed, creating your own regression validation assets.

## Build, Test, and Development Commands
- Create a virtualenv with uv: `uv venv .venv && source .venv/bin/activate`.
- Install runtime deps (numpy, pydantic, TA-Lib bindings): `uv pip install -r requirements.txt`. Install TA-Lib native libs on the host first.
- Run prompt helper: `uv run scripts/gen_indicator_prompt.py` to copy/paste the latest spec.
- Validate code before committing: `uv run scripts/validate_indicator.py` (wraps `pytest`). Use `uv run pytest -k name` for focused debugging.

## Coding Style & Naming Conventions
- Python ≥3.10, 4-space indents, full typing. Classes in `PascalCase`, functions/vars `snake_case`.
- Indicators must inherit `IndicatorBase`, accept a `BaseModel` params object, expose `on_bars(bars: List[list])`, and return `List[IndicatorResultBase]`.
- Bar payloads are simple lists ordered as `[timestamp, open, high, low, close, volume, is_close]`; keep logic deterministic and side-effect free. Add concise docstrings for non-trivial sections.
- Outputs must align 1:1 with input bars; keep `nan` warmups intact. `base.py` exposes the shared BaseModel contract, while concrete result models reside in `ta_indicator.py`.

## Testing Guidelines
- No tests are bundled by default. When adding your own, prefer `pytest` and bar fixtures derived from `BTCUSDT-1m-2025-11.csv`.
- Validate timestamp alignment, value types, boundary behaviors (empty list, short series), and schema errors (missing columns) before shipping changes.

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
