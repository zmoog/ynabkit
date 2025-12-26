.PHONY: test tests clean install lint help

# Default target
help:
	@echo "Available targets:"
	@echo "  make test        - Run all tests"
	@echo "  make tests       - Alias for 'make test'"
	@echo "  make install     - Install package in development mode"
	@echo "  make clean       - Remove build artifacts"
	@echo "  make lint        - Run code quality checks (if configured)"

# Run tests
test:
	@. .venv/bin/activate && python run_tests.py

# Alias for test
tests: test

# Install package in development mode
install:
	@echo "Installing package in development mode..."
	@. .venv/bin/activate && pip install -e .

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	@rm -rf build/
	@rm -rf dist/
	@rm -rf *.egg-info
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete

# Lint (placeholder - add your linting tools here)
lint:
	@echo "Linting not configured yet"
	@echo "You can add tools like: flake8, black, mypy, etc."
