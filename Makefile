.PHONY: up down build logs test lint format clean

#Docker commands

up: 
	docker-compose up -d

down:
	docker-compose down

build:
	docker-compose build

logs:
	docker-compose logs -f

#development commands
format:
	ruff format .
	ruff check --select I --fix .

lint:
	ruff check .
	mypy backend/rc ml/src

test:
	pytest backend/tests ml/tests -v

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +