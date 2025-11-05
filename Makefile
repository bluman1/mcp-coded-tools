.PHONY: help install dev test coverage lint format typecheck clean build publish

help:  ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

install:  ## Install package
	pip install -e .

dev:  ## Install package with development dependencies
	pip install -e ".[dev]"

test:  ## Run tests
	pytest

coverage:  ## Run tests with coverage report
	pytest --cov=mcp_agent_tools --cov-report=html --cov-report=term
	@echo "Coverage report generated in htmlcov/index.html"

lint:  ## Run linting checks
	ruff check src/ tests/ examples/

format:  ## Format code with black
	black src/ tests/ examples/

format-check:  ## Check code formatting
	black --check src/ tests/ examples/

typecheck:  ## Run type checking
	mypy src/

quality:  ## Run all quality checks (format, lint, typecheck)
	@echo "Running format check..."
	@make format-check
	@echo "\nRunning linter..."
	@make lint
	@echo "\nRunning type checker..."
	@make typecheck
	@echo "\n✅ All quality checks passed!"

clean:  ## Clean build artifacts and cache
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build:  ## Build distribution packages
	python -m build

publish-test:  ## Publish to TestPyPI
	twine upload --repository testpypi dist/*

publish:  ## Publish to PyPI
	twine upload dist/*

example-basic:  ## Run basic usage example
	python examples/basic_usage.py

example-advanced:  ## Run advanced agent example (generate tools first)
	python examples/advanced_agent.py generate
	python examples/advanced_agent.py

docs:  ## Generate documentation (if sphinx is set up)
	@echo "Documentation generation not yet configured"

setup-dev:  ## Complete development setup
	@echo "Setting up development environment..."
	python -m venv venv
	@echo "Virtual environment created. Activate it with:"
	@echo "  source venv/bin/activate  (Linux/Mac)"
	@echo "  venv\\Scripts\\activate  (Windows)"
	@echo "\nThen run: make dev"
