# SPDX-License-Identifier: MIT
PYTHON ?= $(if $(wildcard ../.venv/bin/python),../.venv/bin/python,python3)
LATEXMK := latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error

.PHONY: all data view clean distclean
all: downstream.pdf

# Always ask the deterministic generator to check its inputs. It preserves
# unchanged mtimes, so latexmk skips compilation when content is unchanged.
data:
	$(PYTHON) build_tables.py

downstream.pdf: downstream.tex $(wildcard figures/*.tex) build_tables.py data
	$(LATEXMK) downstream.tex

view: downstream.pdf
	open downstream.pdf

clean:
	$(LATEXMK) -c downstream.tex

distclean: clean
	rm -f downstream.pdf
