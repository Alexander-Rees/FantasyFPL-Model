COMPOSE=cd infra && docker compose --env-file ../.env

.PHONY: up down logs ps build test test-unit test-integration

up:
	$(COMPOSE) up -d --build

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f --tail=200

ps:
	$(COMPOSE) ps

build:
	$(COMPOSE) build --no-cache

test: test-unit

test-unit:
	./scripts/test-unit.sh

test-integration:
	./scripts/test-integration-kind.sh
