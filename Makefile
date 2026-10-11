.PHONY: help install install-dev test test-coverage lint format clean build check publish-test publish all

help: ## Show this help message
	@echo "sinhalanorm Development Commands"
	@echo "=========================="
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install the package in development mode
	pip install -e .

install-dev: ## Install development dependencies
	pip install -e ".[dev]"

test: ## Run the test suite
	pytest tests/ -v

test-coverage: ## Run tests with coverage report
	pytest tests/ --cov=sinhalanorm --cov-report=html --cov-report=term

lint: ## Run linting checks
	flake8 sinhalanorm/ tests/
	mypy sinhalanorm/

format: ## Format code with black
	black sinhalanorm/ tests/

clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build: ## Build the package
	python -m build

check: ## Check the built package
	twine check dist/*

publish-test: ## Publish to TestPyPI
	twine upload --repository testpypi dist/*

publish: ## Publish to PyPI
	twine upload dist/*

all: clean install-dev lint test build ## Run all checks and build
