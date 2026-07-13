VENV=.venv
PYTHON=$(VENV)/bin/python
PIP=$(VENV)/bin/pip

.PHONY: dev install test venv

venv:
	python3 -m venv $(VENV)

install: venv
	$(PIP) install -r requirements.txt

dev:
	@echo "Starting production-ready Gunicorn server..."
	@if [ -d "$(VENV)" ]; then \
		$(VENV)/bin/gunicorn app.app:app -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000; \
	else \
		gunicorn app.app:app -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000; \
	fi

test:
	@echo "No tests configured"