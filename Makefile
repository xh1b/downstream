# @ref:calculator-build
# Context: @link:doc-calculator; @link:script-build-calculator; @link:script-serve-calculator. @tag:calculator
PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)
PORT ?= 8000

.PHONY: serve calculator check-calculator
serve:
	$(PYTHON) scripts/serve_calculator.py --port $(PORT)

calculator:
	$(PYTHON) scripts/build_calculator.py

check-calculator:
	$(PYTHON) scripts/build_calculator.py --check

# @ref:docs-build-check
# Contract: @link:development-tooling; @link:script-doccheck. @tag:tooling
.PHONY: check-docs
check-docs:
	$(PYTHON) scripts/refcheck.py check
	$(PYTHON) scripts/tasks.py validate
	$(PYTHON) scripts/doccheck.py --examples --freshness
	$(PYTHON) -m pytest -q tests/test_doccheck.py
