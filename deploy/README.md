# deploy

Production: one Linux server running Docker Compose from a clone of this repository. `docs/RUNBOOK.md` ("Production" and the sections after it) says how to deploy, renew certificates, back up and restore; `make -C deploy help` lists the commands. Adapted from the owner's `kai-app` and `kai-api` projects.

| File | What it is |
| --- | --- |
| `docker-compose.yml` | The production stack: `db`, `api`, `nginx` and, for certificates only, `certbot` |
| `.env.example` | Every value the stack and the scripts read; copied to `deploy/.env` on the server, never committed |
| `Makefile` | The commands run on the server |
| `api.Dockerfile` | The API's image: gunicorn with Uvicorn workers, the catalog and the question bank |
| `web.Dockerfile` | The web app's image: the build, served by nginx |
| `nginx/nginx.conf` | nginx's main configuration: JSON access log, gzip, the rate limit's zone, cache rules, a health server |
| `nginx/app.conf` | The app's locations: static files with the single-page fallback, `/api` proxied to the API, security headers |
| `nginx/default.conf.https` | Server blocks for production: https, with http redirecting to it. `NGINX_CONF_FILE` picks one of the three templates |
| `nginx/default.conf.http` | Server blocks for plain http: a laptop, or a server before its certificate |
| `nginx/default.conf.https.temp` | Server block for the first certificate: certbot's challenge only |
| `certbot/certbot.sh` | The first certificate, and the cron job that renews it |
| `certbot/renew.sh`, `certbot/renew_cron` | The renewal and its cron line |
| `backup.sh`, `backup_cron` | The nightly `pg_dump`, keeping 14, and its cron line |
| `restore.sh` | Replaces the database with one of those dumps |
| `scripts/deploy.sh` | Pull, check nginx, migrate, start, wait until healthy, roll back if not |
| `scripts/check_nginx.sh` | `nginx -t` on the three configurations (CI runs it, through `make check-deploy`) |
| `scripts/install_server.sh` | Docker, git, make and envsubst on a fresh Ubuntu server |

The images are built and published by `.github/workflows/build_publish.yaml` and deployed by `.github/workflows/deploy.yaml`, both run by hand.

Local development does not use this folder: see `docker-compose.yml` at the repository root.
