# Makefile for Sec-Vote Platform

.PHONY: help build up down logs test clean install

help:
	@echo "Sec-Vote Platform - Available Commands:"
	@echo "  make build    - Build all Docker containers"
	@echo "  make up       - Start all services"
	@echo "  make down     - Stop all services"
	@echo "  make logs     - View logs from all services"
	@echo "  make test     - Run tests"
	@echo "  make clean    - Clean up containers and volumes"
	@echo "  make install  - Install Python dependencies locally"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Services are starting..."
	@echo "API Gateway: http://localhost:8080"
	@echo "Health check: http://localhost:8080/health"

down:
	docker-compose down

logs:
	docker-compose logs -f

restart:
	docker-compose restart

test:
	pytest tests/ -v --cov

clean:
	docker-compose down -v
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.db" -delete

install:
	pip install -r requirements.txt

dev-auth:
	cd services/auth && python app.py

dev-poll:
	cd services/poll && python app.py

dev-vote:
	cd services/vote && python app.py

dev-results:
	cd services/results && python app.py

dev-gateway:
	cd gateway && python app.py
