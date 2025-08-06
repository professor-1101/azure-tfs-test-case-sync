.PHONY: install run test clean help

# Default target
help:
	@echo "Available commands:"
	@echo "  install    - Install dependencies"
	@echo "  run        - Run the API server"
	@echo "  test       - Run tests"
	@echo "  test-api   - Run API integration tests"
	@echo "  clean      - Clean up generated files"
	@echo "  help       - Show this help message"

# Install dependencies
install:
	pip install -r requirements.txt

# Run the API server
run:
	python main.py

# Run all tests
test:
	pytest tests/ -v

# Run API integration tests
test-api:
	python test_versioned_api.py

# Clean up generated files
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -f app.log
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -f .coverage

# Development server with auto-reload
dev:
	uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production server
prod:
	uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# Format code
format:
	black app/ tests/ main.py
	isort app/ tests/ main.py

# Lint code
lint:
	flake8 app/ tests/ main.py
	mypy app/ main.py

# Check code quality
check: format lint test 