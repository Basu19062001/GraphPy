DOCKER_COMPOSE=docker-compose
PYTHON=python
PIP=pip
DOCKER=docker

INFO = @echo [INFO]

.PHONY: help build up down logs test lint format install

format:
	$(INFO) "Formatting code with black..."
	$(PYTHON) -m black .