COMPOSE=cd infra && docker compose --env-file ../.env

.PHONY: up down logs ps build

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
