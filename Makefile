# Every target here is a check you can run and read the result of.
# `make check` is the gate before any submission.

PAPER_DIR := paper
MAIN      := main
BIB       := $(PAPER_DIR)/refs.bib
# A project venv (.venv) is used when it exists: experiments and figures
# often need packages, such as matplotlib, that the system Python lacks.
PYTHON    := $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)

.PHONY: help paper figures tables check check-refs check-refs-fresh scrub \
        find-refs ledger pdfs check-extractions check-results check-evidence clean distclean test

help:
	@echo "Targets:"
	@echo "  make paper        compile the PDF (latexmk)"
	@echo "  make figures      regenerate figures from experiments/results/"
	@echo "  make tables       regenerate LaTeX tables from experiments/results/"
	@echo "  make check-refs   verify every reference against Crossref/arXiv/OpenAlex"
	@echo "  make scrub        find leftover AI text, placeholders, unknown cite keys"
	@echo "  make check        tables, figures, refs, results, extractions, evidence, ledger, scrub, paper (the gate)"
	@echo "  make find-refs Q=<doi|arxiv id|title>   look up a real reference"
	@echo "  make ledger       show claims that have no evidence file yet"
	@echo "  make pdfs         download open-access PDFs for refs.bib into sources/"
	@echo "  make check-extractions   every quote in notes/extractions/ is in its PDF"
	@echo "  make check-results       every result file names its commit, seed and data"
	@echo "  make check-evidence      every cited sentence has a quote that is in its PDF"
	@echo "  make test         run the tool self-tests"
	@echo "  make clean        remove LaTeX build files"

# latexmk if available, otherwise plain pdflatex with a bibtex pass.
paper:
	@cd $(PAPER_DIR) && if command -v latexmk >/dev/null 2>&1; then \
		latexmk -pdf -interaction=nonstopmode -halt-on-error $(MAIN).tex; \
	else \
		echo "latexmk not found, falling back to pdflatex"; \
		pdflatex -interaction=nonstopmode -halt-on-error $(MAIN).tex && \
		(bibtex $(MAIN) || true) && \
		pdflatex -interaction=nonstopmode -halt-on-error $(MAIN).tex && \
		pdflatex -interaction=nonstopmode -halt-on-error $(MAIN).tex; \
	fi

figures:
	$(PYTHON) analysis/make_figures.py

tables:
	$(PYTHON) analysis/make_tables.py

check-refs:
	$(PYTHON) tools/check_refs.py $(BIB)

# Ignore the cache: use this for the final pre-submission run.
check-refs-fresh:
	$(PYTHON) tools/check_refs.py $(BIB) --no-cache

scrub:
	$(PYTHON) tools/scrub.py $(PAPER_DIR) --strict

find-refs:
	@test -n "$(Q)" || (echo 'Usage: make find-refs Q="<doi|arxiv id|title>"'; exit 2)
	$(PYTHON) tools/find_refs.py "$(Q)" --append

ledger:
	@$(PYTHON) tools/check_ledger.py

pdfs:
	$(PYTHON) tools/fetch_pdfs.py $(BIB)

check-extractions:
	$(PYTHON) tools/check_extractions.py notes/extractions

check-results:
	$(PYTHON) tools/check_results.py experiments/results

check-evidence:
	$(PYTHON) tools/check_evidence.py paper/sections

# The pre-submission gate. Any failure stops the chain.
check: tables figures check-refs-fresh check-results check-extractions check-evidence ledger scrub paper
	@echo
	@echo "All checks passed. Still your job before submitting:"
	@echo "  - confirm the abstract and contribution claims are yours"
	@echo "  - write the AI disclosure your venue wants (see docs/venues.md)"
	@echo "  - read ai_use_log.md once more"

test:
	@echo "== check_refs on the test fixture (expect 2 verified, 3 bad, exit 1) =="
	-$(PYTHON) tools/check_refs.py tools/tests/sample.bib --no-cache
	@echo
	@echo "== scrub on the dirty fixture (expect 7 blocking, exit 1) =="
	-$(PYTHON) tools/scrub.py tools/tests/dirty --strict
	@echo
	@echo "Self-tests done. Both tools are expected to exit non-zero above."

clean:
	cd $(PAPER_DIR) && latexmk -C || true
	rm -f $(PAPER_DIR)/*.bbl $(PAPER_DIR)/*.blg $(PAPER_DIR)/*.aux

distclean: clean
	rm -rf .cache
