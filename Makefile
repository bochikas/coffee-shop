THIS_FILE := $(lastword $(MAKEFILE_LIST))
.PHONY: build up

build:
	docker compose -f docker-compose.yml up --build -d
up:
	docker compose -f docker-compose.yml up -d
