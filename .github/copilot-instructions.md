# Copilot instructions for lmt-analysis

This file gives concise, actionable guidance for AI coding agents working on this repository.

- **Big picture:** This project is an analysis library for Live Mouse Tracker outputs. Core code lives under [LMT/lmtanalysis](../LMT/lmtanalysis) and consumes `.sqlite` tracking databases to produce detections, events, measures and plots (see [README.md](../README.md)).

- **Primary inputs / outputs:** Agents should assume inputs are `.sqlite` files (openable via GUI helpers in [LMT/lmtanalysis/FileUtil.py](../LMT/lmtanalysis/FileUtil.py)). Outputs are plot images and computed event tables; many example flows are in notebooks under `LMT/`.

- **Major components:**
  - Data & utilities: [LMT/lmtanalysis/FileUtil.py](../LMT/lmtanalysis/FileUtil.py), [LMT/lmtanalysis/Util.py](../LMT/lmtanalysis/Util.py)
  - Core domain types: files like [LMT/lmtanalysis/Detection.py](../LMT/lmtanalysis/Detection.py), [LMT/lmtanalysis/Event.py](../LMT/lmtanalysis/Event.py), [LMT/lmtanalysis/Mask.py](../LMT/lmtanalysis/Mask.py)
  - Event builders: many independent modules named `BuildEvent*.py` under [LMT/lmtanalysis](../LMT/lmtanalysis) — they implement specific event-detection logic and are intentionally modular.
  - Logging / metadata: [LMT/lmtanalysis/TaskLogger.py](../LMT/lmtanalysis/TaskLogger.py) writes/reads a `LOG` table in the sqlite DB.

- **Conventions & patterns to follow:**
  - New event logic should follow existing `BuildEvent*.py` structure (stateless functions operating on detection data). Look at `BuildEventMove.py` and `BuildEventGroup2.py` for examples.
  - Many modules use simple procedural code and global functions (no type hints). Keep changes stylistically consistent unless refactoring across the codebase.
  - Example scripts in `LMT/examples/` are often named with numeric prefixes (e.g. `001_draw_trajectory.py`) — these are intended to be run as scripts/not imported as modules (leading digits break normal import names).
  - GUI interactions use `tkinter` dialogs; tests or CI runs must avoid executing GUI dialogs (mock or bypass `FileUtil` helpers when writing automated checks).

- **Setup / developer workflows (discoverable):**
  - Dependencies are listed in `python packages needed.txt`. To create an environment and install them (from repo root):

```bash
conda create -n lmt python=3.8 -y
conda activate lmt
xargs -a "python packages needed.txt" pip install
```

  - Notebooks: open `LMT/Live Mouse Tracker Analysis.ipynb` (../LMT/Live Mouse Tracker Analysis.ipynb) for canonical examples and exploratory workflows.
  - Running examples: run scripts directly from the repository root, e.g.: `python LMT/examples/001_draw_trajectory.py` (these scripts expect a desktop environment because of `tkinter`).

- **Testing / debugging tips:**
  - There is no formal test suite in the repo. Use the notebooks and `examples/` scripts to validate behavior.
  - For debugging DB-related code, inspect the `LOG` table created/used by `TaskLogger` and open `.sqlite` files with `sqlite3` or DB browser.
  - Prefer small, local changes when adding features; many modules touch sqlite schemas or expected DB contents.

- **Integration points / external deps:**
  - SQLite database files (Live Mouse Tracker output) are the canonical input format.
  - Heavy usage of numpy/pandas/matplotlib/networkx — see `python packages needed.txt` for the minimal list.

- **When to open a PR vs a branch note:**
  - Bugfixes or additions to a single `BuildEvent*.py` or utility: single-file PR with explanation and reproduction using one of the example `.sqlite` files or a small synthetic dataset.
  - Cross-cutting changes (API, long refactors): open an issue first; these modules are widely used by notebooks and examples.

If any section is unclear or you'd like more detail (for example, a checklist for adding a new `BuildEvent`), tell me which area to expand.
