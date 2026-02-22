# Variables
DOCKER_COMPOSE = docker compose
PROD_COMPOSE = docker compose -f docker-compose.prod.yml

.PHONY: help up down build logs restart migrate makemigrations collectstatic schema dlogs tail-backend tail-ai clean prod-up prod-down prod-logs prod-restart prod-migrate prod-dlogs

help:
	@echo "Dev Commands:"
	@echo "  make up             - Start dev services"
	@echo "  make logs           - Show dev logs"
	@echo ""
	@echo "Production Commands (Scan2Home):"
	@echo "  make prod-up        - Start production stack (detached)"
	@echo "  make prod-down      - Stop production stack"
	@echo "  make prod-logs      - Tail all production logs"
	@echo "  make prod-restart   - Restart production services"
	@echo "  make prod-migrate   - Run production migrations"
	@echo "  make prod-dlogs     - Tail live production request logs"
	@echo ""
	@echo "Common Utilities:"
	@echo "  make clean          - Remove pycache and temp files"

# ─── DEVELOPMENT ──────────────────────────────────────────
up:
	$(DOCKER_COMPOSE) up -d
logs:
	$(DOCKER_COMPOSE) logs -f

# ─── PRODUCTION ───────────────────────────────────────────
prod-up:
	$(PROD_COMPOSE) up -d
prod-down:
	$(PROD_COMPOSE) down
prod-logs:
	$(PROD_COMPOSE) logs -f
prod-restart:
	$(PROD_COMPOSE) restart
prod-migrate:
	$(PROD_COMPOSE) exec backend python manage.py migrate
prod-dlogs:
	$(PROD_COMPOSE) exec backend tail -f logs/requests.log

# ─── UTILITIES ────────────────────────────────────────────
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
