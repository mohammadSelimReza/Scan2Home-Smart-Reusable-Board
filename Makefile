# Variables
DOCKER_COMPOSE = docker compose
PROD_COMPOSE = docker compose -f docker-compose.prod.yml

.PHONY: help up down build logs restart migrate makemigrations shell createsuperuser test seed clean prod-up prod-down prod-logs prod-restart prod-migrate prod-shell prod-createsuperuser prod-seed prod-dlogs dlog

help:
	@echo "Dev Commands:"
	@echo "  make up             - Start dev services"
	@echo "  make logs           - Show dev logs"
	@echo "  make shell          - Enter Django shell (dev)"
	@echo "  make createsuperuser - Create admin user (dev)"
	@echo "  make migrate        - Run migrations (dev)"
	@echo "  make makemigrations - Generate migrations (dev)"
	@echo "  make seed           - Populate dummy data (dev)"
	@echo "  make test           - Run backend tests"
	@echo ""
	@echo "Production Commands (Scan2Home):"
	@echo "  make prod-up        - Start production stack"
	@echo "  make prod-down      - Stop production stack"
	@echo "  make prod-logs      - Tail all production logs"
	@echo "  make prod-shell     - Enter Django shell (prod)"
	@echo "  make prod-createsuperuser - Create admin user (prod)"
	@echo "  make prod-migrate   - Run production migrations"
	@echo "  make prod-seed      - Populate dummy data (prod)"
	@echo "  make prod-dlogs     - Tail live request logs (prod)"
	@echo ""
	@echo "Common Utilities:"
	@echo "  make clean          - Remove pycache and temp files"

# ─── DEVELOPMENT ──────────────────────────────────────────
up:
	$(DOCKER_COMPOSE) up -d
logs:
	$(DOCKER_COMPOSE) logs -f
shell:
	$(DOCKER_COMPOSE) exec backend python manage.py shell
createsuperuser:
	$(DOCKER_COMPOSE) exec backend python manage.py createsuperuser
migrate:
	$(DOCKER_COMPOSE) exec backend python manage.py migrate
makemigrations:
	$(DOCKER_COMPOSE) exec backend python manage.py makemigrations
test:
	$(DOCKER_COMPOSE) exec backend pytest
seed:
	$(DOCKER_COMPOSE) exec backend python manage.py populate_dummy_data --count 100

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
prod-shell:
	$(PROD_COMPOSE) exec backend python manage.py shell
prod-createsuperuser:
	$(PROD_COMPOSE) exec backend python manage.py createsuperuser
prod-seed:
	$(PROD_COMPOSE) exec backend python manage.py populate_dummy_data --count 50
prod-dlogs:
	$(PROD_COMPOSE) exec backend tail -f logs/requests.log
dlog: prod-dlogs

# ─── UTILITIES ────────────────────────────────────────────
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
