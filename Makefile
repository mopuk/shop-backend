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
		$(PYTHON) -m flask --app app run --port 5000; \
	else \
		python3 -m flask --app app run --port 5000; \
	fi

test:
	@echo "No tests configured"