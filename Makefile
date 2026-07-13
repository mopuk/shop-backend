VENV=.venv
PYTHON=$(VENV)/bin/python
PIP=$(VENV)/bin/pip

.PHONY: dev install test venv

venv:
	python3 -m venv $(VENV)

install: venv
	$(PIP) install -r requirements.txt

dev:
	@echo "Starting development server..."
	@if [ -d "$(VENV)" ]; then \
		$(PYTHON) -m fastapi dev; \
	else \
		python3 -m fastapi dev; \
	fi

test:
	@echo "No tests configured"