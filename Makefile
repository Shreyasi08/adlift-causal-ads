.PHONY: setup sim analyze report dashboard all test lint
PY = uv run python

setup:
	uv sync --all-extras

sim:
	$(PY) pipelines/run_simulation.py

analyze:
	$(PY) pipelines/run_phase1.py

report:
	@echo "report: implemented in M6/M7"

dashboard:
	uv run streamlit run dashboard/app.py

all: sim analyze report

test:
	uv run pytest -q

lint:
	uv run ruff check . && uv run ruff format --check .
