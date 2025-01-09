.PHONY: setup run clean check-domains help test lint format install-dev

help:
	@echo "Available commands:"
	@echo "  make setup         - Create virtual environment and install dependencies"
	@echo "  make install-dev   - Install package in development mode with dev dependencies"
	@echo "  make run          - Run the domain checker in interactive mode"
	@echo "  make check-domains - Check domains from domains.txt file"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run linters (flake8, mypy)"
	@echo "  make format       - Format code (black, isort)"
	@echo "  make clean        - Remove virtual environment and cache files"

setup:
	python3 -m venv venv
	. venv/bin/activate && pip install -r requirements.txt

install-dev: setup
	. venv/bin/activate && pip install -r requirements-dev.txt
	. venv/bin/activate && pip install -e .

run:
	. venv/bin/activate && PYTHONPATH=src PYTHONUNBUFFERED=1 python -m domain_checker.main

check-domains:
	. venv/bin/activate && PYTHONPATH=src PYTHONUNBUFFERED=1 python -m domain_checker.main domains.txt

test: install-dev
	. venv/bin/activate && PYTHONPATH=src python -m pytest tests/ -v

lint: install-dev
	. venv/bin/activate && flake8 src/domain_checker
	. venv/bin/activate && mypy src/domain_checker

format: install-dev
	. venv/bin/activate && black src/domain_checker tests
	. venv/bin/activate && isort src/domain_checker tests

clean:
	rm -rf venv
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete 