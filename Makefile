.PHONY: help build up down logs clean dev prod restart rebuild

# Default target
help:
	@echo "Career Coach AI - Docker Management"
	@echo ""
	@echo "Available commands:"
	@echo "  make build     - Build all Docker images"
	@echo "  make up        - Start the application in production mode"
	@echo "  make dev       - Start the application in development mode"
	@echo "  make down      - Stop and remove containers"
	@echo "  make logs      - View application logs"
	@echo "  make restart   - Restart the application"
	@echo "  make rebuild   - Rebuild and restart the application"
	@echo "  make clean     - Remove all containers, images, and volumes"

# Build all images
build:
	docker-compose build

# Start in production mode
up:
	docker-compose up -d

# Start in development mode
dev:
	docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d

# Stop containers
down:
	docker-compose down

# View logs
logs:
	docker-compose logs -f

# Restart application
restart:
	docker-compose restart

# Rebuild and restart
rebuild: down build up

# Clean everything
clean:
	docker-compose down -v --rmi all --remove-orphans
	docker system prune -f

# Backend specific commands
backend-logs:
	docker-compose logs -f backend

frontend-logs:
	docker-compose logs -f frontend

# Development helpers
backend-shell:
	docker-compose exec backend /bin/bash

frontend-shell:
	docker-compose exec frontend /bin/sh

# Health check
health:
	@echo "Checking application health..."
	@curl -f http://localhost:8000/ || echo "Backend not responding"
	@curl -f http://localhost:3000/ || echo "Frontend not responding" 

# Testing commands
test:
	@echo "Running all tests..."
	pytest tests/ -v --cov=. --cov-report=term-missing

test-unit:
	@echo "Running unit tests..."
	pytest tests/unit/ -v --cov=. --cov-report=term-missing

test-integration:
	@echo "Running integration tests..."
	pytest tests/integration/ -v --cov=. --cov-report=term-missing

test-coverage:
	@echo "Running tests with coverage report..."
	pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing

test-fast:
	@echo "Running tests without coverage..."
	pytest tests/ -v

lint:
	@echo "Running linting..."
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

lint-and-test: lint test 