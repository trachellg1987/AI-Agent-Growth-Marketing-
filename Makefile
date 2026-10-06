# ai-growth-agents-for-marketers
# Run `make help` for targets. Nothing here calls a real model except `make run`
# without --dry-run / --stats-only.

PY ?= python3
AGENT ?=
ARGS ?=
NAME ?=
PYTHON ?=
MARKDOWNLINT ?= npx --yes markdownlint-cli@0.45.0

.PHONY: help setup validate unit refs examples examples-update smoke test test-api list run scaffold lint clean

help:
	@echo "Targets:"
	@echo "  setup            install Python dependencies"
	@echo "  validate         check repo structure and content rules"
	@echo "  smoke            run every agent offline (--help, --dry-run, --stats-only)"
	@echo "  test             validate + unit tests + reference check + example check + smoke"
	@echo "  test-api         run agents against a local fake model API (needs make setup)"
	@echo "  list             list agents"
	@echo "  run              make run AGENT=08-ab-test-analyzer ARGS=\"--stats-only\""
	@echo "  scaffold         make scaffold NAME=my-agent [PYTHON=1]"
	@echo "  examples-update  rewrite computed blocks in the docs from fresh runs"
	@echo "  lint             markdownlint + Python byte-compile"
	@echo "  clean            remove caches"

setup:
	$(PY) -m pip install -r requirements.txt

validate:
	$(PY) scripts/validate.py

unit:
	$(PY) -m unittest discover -s tests -t . -v

refs:
	$(PY) tests/reference_check.py

examples:
	$(PY) scripts/check_examples.py

examples-update:
	$(PY) scripts/check_examples.py --update

smoke:
	$(PY) scripts/smoke_test.py

test: validate unit refs examples smoke

test-api:
	$(PY) scripts/api_contract_test.py

list:
	@for d in [0-9][0-9]-*/; do \
		d=$${d%/}; \
		if [ -f "$$d/agent.py" ]; then kind="python"; else kind="prompt"; fi; \
		printf "%-28s %s\n" "$$d" "$$kind"; \
	done

run:
	@if [ -z "$(AGENT)" ]; then echo "usage: make run AGENT=08-ab-test-analyzer ARGS=\"--stats-only\""; exit 2; fi
	@if [ ! -f "$(AGENT)/agent.py" ]; then echo "$(AGENT) has no agent.py (prompt-only agent: open $(AGENT)/prompt.md)"; exit 2; fi
	$(PY) $(AGENT)/agent.py $(ARGS)

scaffold:
	@if [ -z "$(NAME)" ]; then echo "usage: make scaffold NAME=my-agent [PYTHON=1]"; exit 2; fi
	$(PY) scripts/scaffold_agent.py --name $(NAME) $(if $(PYTHON),--python,)

lint:
	$(MARKDOWNLINT) "**/*.md" ".agents/*.md" ".github/**/*.md" --ignore node_modules
	$(PY) -m compileall -q common scripts skills tests examples $(wildcard [0-9][0-9]-*)

clean:
	find . -name "__pycache__" -type d -prune -exec rm -rf {} +
	rm -rf .pytest_cache .mypy_cache
