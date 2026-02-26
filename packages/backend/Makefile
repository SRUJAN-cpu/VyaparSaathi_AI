.PHONY: setup test lint format clean

setup:
	python -m venv .venv
	.venv/bin/pip install -r requirements-dev.txt
	.venv/bin/pip install -e .

test:
	.venv/bin/pytest

lint:
	.venv/bin/flake8 src tests
	.venv/bin/mypy src

format:
	.venv/bin/black src tests

format-check:
	.venv/bin/black --check src tests

clean:
	rm -rf .venv build dist *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
