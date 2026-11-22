# Before the first deploy

What to get, decide and set up before CaramelCase goes on a server. The production files are ready and were tried on a laptop, but nothing has been deployed and the build and deploy workflows have never run.

This is a checklist. The procedures themselves are in `docs/RUNBOOK.md`: "First deploy" is the step-by-step that follows this list, and the sections after it cover certificates, backups and logs. `deploy/README.md` says what each production file is.

To rehearse first, run the production stack on your laptop: `docs/RUNBOOK.md`, "Trying the production stack on a laptop".

## 1. CI must be green

- [ ] The latest commit on `main` passes every CI job in GitHub Actions, the end-to-end job included.

The "Build and publish images" workflow runs CI first and builds nothing from a commit that fails it.

## 2. Accounts and decisions

| Item | Required | What to do |
| --- | --- | --- |
| A server | Yes | One Linux server, Ubuntu (`deploy/scripts/install_server.sh` is written for it and was tried on 24.04). Ports 22, 80 and 443 open. DigitalOcean or AWS is still to be decided. Nothing has been load-tested, so start small. |
| A domain | Yes | An A record pointing the domain at the server's address. Only the domain itself is served, not `www.`. If you add an AAAA (IPv6) record, the server must answer on IPv6 too, or Let's Encrypt's check can fail. |
| Docker Hub | Yes | An account and an access token with read and write access. The build workflow pushes `<user>/caramelcase-api` and `<user>/caramelcase-web`, named after the GitHub repository. Keep the **API image private**: it contains the whole question bank with the answers, which the app otherwise only serves a few questions at a time. The web image contains only the built site, which anyone can download from the site anyway. Check how many private repositories your Docker Hub plan allows. |
| SMTP | Yes, for email sign-in | Host, port (587, STARTTLS), username, password and a From address. Without them nobody can sign in by email; guests can still play. Set up SPF and DKIM for the sending domain with your email provider, so sign-in links do not land in spam. |
| Google sign-in | Optional | An OAuth client of type "Web application" in Google Cloud, with `https://<DOMAIN>/api/v1/auth/google/callback` as its redirect URI. While its consent screen is in "Testing", only the test users you list can sign in. Without it there is no Google button. |
| A Let's Encrypt email | Yes | Any address you read: `CERTBOT_EMAIL`. |
| Better Stack, Plausible | Optional | Better Stack for error tracking, and if you want them, uptime monitoring and log collection; Plausible for analytics. Error tracking and analytics stay off until their keys are set. Before switching on error tracking, analytics or log collection, add the service to the privacy policy (`docs/RUNBOOK.md`, "Logs and monitoring"). |

## 3. GitHub secrets

- [ ] Set in the repository's Settings, "Secrets and variables", "Actions": `DOCKER_HUB_USERNAME`, `DOCKER_HUB_TOKEN`, `VM_HOST`, `VM_USER`, `VM_SSH_PRIVATE_KEY`, `PROJECT_ROOT`, and optionally `VITE_BETTER_STACK_ERRORS_DSN`, `VITE_PLAUSIBLE_DOMAIN`, `VITE_PLAUSIBLE_SCRIPT`.

`docs/RUNBOOK.md`, "The workflows' secrets", says what each one is.

## 4. The server

`install_server.sh` installs Docker, git, make and envsubst. It does not set up the following, which the deploy workflow needs:

- [ ] **A user for deploys**, the one named in `VM_USER`. Its SSH public key goes in its `~/.ssh/authorized_keys`, and the private key goes in the `VM_SSH_PRIVATE_KEY` secret.
- [ ] **Docker access for that user:** `sudo usermod -aG docker <user>`, then sign in again. The workflow runs `docker` without `sudo`.
- [ ] **A clone that belongs to that user**, at `PROJECT_ROOT`, because the workflow runs `git pull` as that user. For example: `sudo mkdir /opt/caramelcase && sudo chown <user>: /opt/caramelcase`, then `git clone` as the user. If the GitHub repository is private, the server needs a read-only deploy key for that user.
- [ ] **`deploy/.env`**, copied from `deploy/.env.example` and filled in by that user. At least:
  - `DOCKER_IMAGE_API`, `DOCKER_IMAGE_WEB`: the two image names from step 2
  - `DOMAIN`, `CERTBOT_EMAIL`, `PROJECT_ROOT`
  - `POSTGRES_PASSWORD`: letters and digits only, for example `openssl rand -hex 24`
  - `APP_BASE_URL` and `CORS_ORIGINS`: both `https://<DOMAIN>`
  - `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `EMAIL_FROM`
  - optionally `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `BETTER_STACK_ERRORS_DSN`
- [ ] **`docker login`** as that user, if any image is private.

## 5. The order that matters

- [ ] **Publish the images before the certificate step.** In Actions, run "Build and publish images" on `main` before `sudo make -C deploy certificate`, because that step starts nginx from the web image. If the web image is private, first pull it as the deploy user (`cd deploy && docker compose pull nginx`): the certificate step runs as root, which has no Docker Hub login, but it can use an image already on the server.
- [ ] Then follow `docs/RUNBOOK.md`, "First deploy", steps 1 to 10. Later deploys are two workflow runs: "Later deploys" in the same file.

## 6. Before students arrive

These do not block a deploy, but they block opening the app to students:

- [ ] **A hand check of about 50 questions per launch subject**, then publish each subject. Students see no subject until it is published (`docs/RUNBOOK.md`, "Publishing a subject").
- [ ] **The legal text.** The privacy policy and the terms are placeholders with gaps in brackets and a "draft" note (`docs/RUNBOOK.md`, "Privacy policy and terms").
- [ ] **Where backups go.** They are kept 14 days on the server's own disk only, so losing the server loses them too (`docs/RUNBOOK.md`, "Backup and restore").
- [ ] **Uptime monitors** in Better Stack on `https://<DOMAIN>/api/v1/health` and `https://<DOMAIN>/`, and heartbeats for the backup and renewal cron jobs (optional; `docs/RUNBOOK.md`, "Uptime monitoring with Better Stack").
- [ ] **Log collection** to Better Stack, so the logs outlive the server (optional; `docs/RUNBOOK.md`, "Log collection with Better Stack").

`docs/PLAN.md`, "Still needed from the owner", has the full list of open items, including those that do not concern the deploy.
