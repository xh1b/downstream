# SPDX-License-Identifier: MIT
# Copyright (c) 2026 John Larue
#
# Build the paper: `make` produces downstream.pdf from downstream.tex.

LATEXMK := latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error

.PHONY: all view clean distclean

all: downstream.pdf

downstream.pdf: downstream.tex
	$(LATEXMK) downstream.tex

view: downstream.pdf
	open downstream.pdf

clean:
	$(LATEXMK) -c downstream.tex

distclean: clean
	rm -f downstream.pdf
