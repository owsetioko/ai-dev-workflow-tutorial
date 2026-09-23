# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Two things share this repo:

- **A tutorial** (`README.md`, `pre-work-setup.md`, `workshop-build-deploy.md`, `codex-companion.md`, `capstone-tools.md`) that teaches a PRD → `TASKS.md` → brainstorming → writing-plans → executing-plans → deploy workflow using Superpowers skills.
- **The dashboard built by following it**: a Streamlit app for ShopSmart sales, specified in `prd/ecommerce-analytics.md`, reading `data/sales-data.csv`.

## Commands

All commands use the project venv in `venv/` (dependencies in `requirements.txt`, no uv/conda).

```bash
python3 -m venv venv && venv/bin/pip install -r requirements.txt   # set up
venv/bin/python -m pytest -v                                        # all tests
venv/bin/python -m pytest tests/test_data.py::test_total_sales -v   # one test
source venv/bin/activate && streamlit run app.py                    # run the app (http://localhost:8501)
```

- Stop any old server before starting a new one: `pkill -f "streamlit run app.py"`.
- When starting Streamlit from a non-interactive shell, add `--server.headless true`. Otherwise its first-run email prompt blocks and the process exits.
- To check the page renders without a browser, use `streamlit.testing.v1.AppTest`:
  ```bash
  venv/bin/python -c "from streamlit.testing.v1 import AppTest; at = AppTest.from_file('app.py').run(); print(len(at.exception), [m.value for m in at.metric])"
  ```
  Expected: `0 ['$116,500', '482']`.

## Architecture

- **`data.py`** holds pure pandas loading and calculation functions and must never import Streamlit. That is what lets `tests/test_data.py` test every number without starting the app. New calculations go here, test-first.
- **`app.py`** holds only layout and Plotly charts. It calls `data.py`, caches the CSV with `@st.cache_data`, and on `FileNotFoundError` shows `st.error` then `st.stop()`.
- **`DATA_PATH`** in `data.py` is absolute (built from `__file__`), so the app and tests work from any working directory. Keep it that way.
- **`data.py` next to the `data/` folder:** `import data` resolves to the module because a module file takes priority over a namespace-package directory. If `data.py` is missing, the import error says "(unknown location)".
- **`pytest.ini`** sets `pythonpath = .` so tests can `import data`.
- **Horizontal bar charts** use `categoryorder="total ascending"` so the largest bar is at the top, because Plotly draws category axes from the bottom up.
- **Tests run against the real CSV.** The expected values (482 orders, $116,500.21 total, Electronics top category, regions ordered North/West/East/South) were computed from `data/sales-data.csv`. If the data file changes, these tests must change with it.

## Workflow conventions

- **`TASKS.md`** is the milestone board (TASK-1 to TASK-5). Milestones move To Do → In Progress → Done. When a milestone is done, tick its criteria and its own copy of the Definition of Done (never the shared list at the top), and add a `Commit:` line with the hash of the last code commit.
- **Every commit message starts with its milestone ID**, e.g. `TASK-3: Add monthly sales trend chart`.
- **Design specs and plans** live in `docs/superpowers/specs/` and `docs/superpowers/plans/`. The plan numbers its units "Plan Step N" so they aren't confused with TASK-N, and each step is labelled with its milestone. The Superpowers `task-start`/`task-done` scripts expect `### Task N` headings and won't parse this plan, so track progress by hand.
- **Branches:** work on the feature branch `feature/sales-dashboard`, with no git worktrees. Deployment to Streamlit Community Cloud is the user's step, done from `main` after merging. Don't mark TASK-5 done until there is a public URL.
- **`.gitignore`** keeps `dev/` local (instructor notes), but `docs/` must stay tracked.
