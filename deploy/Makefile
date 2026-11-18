# Production commands, run on the server in deploy/ (or `make -C deploy
# <target>` from the repository). docker compose reads deploy/.env;
# docs/RUNBOOK.md says when to run what.

COMPOSE = docker compose
# A one-off container of the API's image: the code and the question bank
# of the deployed commit, against the running database.
RUN_API = $(COMPOSE) run --rm --no-deps api

.PHONY: help build up down ps logs deploy migrate seed import-content \
	publish backup backup-cron certificate check-nginx psql

help:
	@echo "make deploy          pull the images, migrate, restart, check (scripts/deploy.sh)"
	@echo "make up              start every service and wait until healthy"
	@echo "make down            stop them; the database stays in its volume"
	@echo "make ps / logs       state and logs of the services"
	@echo "make migrate         apply the database migrations"
	@echo "make seed            plans, flags, subjects and topics"
	@echo "make import-content  bring the questions in line with the image's bank"
	@echo "                     (args=--dry-run to see the counts first)"
	@echo "make publish s=slug  publish a subject and its verified questions"
	@echo "make backup          dump the database now (backup.sh)"
	@echo "make backup-cron     install the nightly backup (as root)"
	@echo "make certificate     the first TLS certificate and its renewal (as root)"
	@echo "make check-nginx     nginx -t on the three configurations"
	@echo "make psql            a psql prompt on the database"
	@echo "make build           build both images here, to try the stack on a laptop"

build:
	$(COMPOSE) build

up:
	$(COMPOSE) up -d --wait

down:
	$(COMPOSE) down

ps:
	$(COMPOSE) ps

logs:
	$(COMPOSE) logs -f --tail 100

deploy:
	./scripts/deploy.sh

migrate:
	$(COMPOSE) up -d --wait db
	$(RUN_API) alembic upgrade head

seed:
	$(RUN_API) python -m app.cli seed

import-content:
	$(RUN_API) python -m app.cli import-content $(args)

publish:
	@test -n "$(s)" || { echo 'usage: make publish s="estruturas-de-dados"'; exit 1; }
	$(RUN_API) python -m app.cli publish-subjects $(s)

backup:
	./backup.sh

backup-cron:
	set -a && . ./.env && set +a && \
		envsubst '$${PROJECT_ROOT}' < backup_cron > /etc/cron.d/caramelcase_backup
	chmod 644 /etc/cron.d/caramelcase_backup

certificate:
	./certbot/certbot.sh

check-nginx:
	./scripts/check_nginx.sh

psql:
	$(COMPOSE) exec db sh -c 'psql -U "$$POSTGRES_USER" -d "$$POSTGRES_DB"'
