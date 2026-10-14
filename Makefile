PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)
PORT ?= 8000

.PHONY: serve calculator check-calculator
serve:
	$(PYTHON) scripts/serve_calculator.py --port $(PORT)

calculator:
	$(PYTHON) scripts/build_calculator.py

check-calculator:
	$(PYTHON) scripts/build_calculator.py --check
