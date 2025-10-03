.PHONY: help test lint format check-format coverage clean install install-dev
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "FIRM-Core Development Tools"
	@echo "=========================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -e .

install-dev: ## Install development dependencies
	pip install -e ".[dev]"

test: ## Run test suite
	pytest -q

test-verbose: ## Run test suite with verbose output
	pytest -v

test-coverage: ## Run tests with coverage report
	pytest --cov=FIRM_dsl --cov=FIRM_constants --cov=FIRM_zx --cov=FIRM_clifford --cov=FIRM_audio --cov=FIRM_ui --cov-report=term-missing --cov-report=html

lint: ## Run linting checks
	flake8 FIRM_dsl/ FIRM_constants/ FIRM_zx/ FIRM_clifford/ FIRM_audio/ FIRM_ui/ tests/
	@echo "✓ Linting passed"

format: ## Format code with black and isort
	black FIRM_dsl/ FIRM_constants/ FIRM_zx/ FIRM_clifford/ FIRM_audio/ FIRM_ui/ tests/
	isort FIRM_dsl/ FIRM_constants/ FIRM_zx/ FIRM_clifford/ FIRM_audio/ FIRM_ui/ tests/
	@echo "✓ Code formatted"

check-format: ## Check if code is properly formatted
	black --check FIRM_dsl/ FIRM_constants/ FIRM_zx/ FIRM_clifford/ FIRM_audio/ FIRM_ui/ tests/
	isort --check-only FIRM_dsl/ FIRM_constants/ FIRM_zx/ FIRM_clifford/ FIRM_audio/ FIRM_ui/ tests/
	@echo "✓ Format check passed"

generate-constants: ## Generate constants header from derivations
	python3 -c "from FIRM_constants.generate_header import build_constants_from_derivations, render_header; constants = build_constants_from_derivations([2, 4, 8]); print('Generated constants:'); [print(f'  {k}: {v.value} (proof: {v.proof_id})') for k, v in constants.items()] if constants else print('  None (derivations not yet implemented)')"

validate-theory: ## Run theory validation tests only
	pytest -m theory -v

pre-commit-install: ## Install pre-commit hooks
	pre-commit install

pre-commit-run: ## Run pre-commit on all files
	pre-commit run --all-files

clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

benchmark: ## Run performance benchmarks
	pytest -m benchmark --benchmark-only

integration: ## Run integration tests
	pytest -m integration -v

deploy-check: ## Run deployment validation checks
	@echo "Running deployment validation..."
	pytest -m "theory or integration" -q
	make check-format
	make lint
	make generate-constants
	@echo "✓ Deployment validation passed"

check-all: check-format lint test ## Run all checks (format, lint, test)
	@echo "✓ All checks passed"
