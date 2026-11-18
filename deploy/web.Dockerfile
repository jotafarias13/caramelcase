# The web app, built, and nginx to serve it. Built from the repository
# root, which .dockerignore narrows down:
#
#   docker build -f deploy/web.Dockerfile .
#
# nginx's configuration is not in the image: deploy/docker-compose.yml
# mounts it from deploy/nginx/, the same way in every mode.

FROM node:24-slim AS build

WORKDIR /app/web
COPY web/package.json web/package-lock.json ./
RUN npm ci --no-audit --no-fund

# web/ reads the design handoff in place, at ../design.
COPY design/ /app/design/
COPY web/ ./

# Optional keys, read at build time by src/lib/monitoring.ts. Empty means
# off: the build then holds no code of either service.
ARG VITE_SENTRY_DSN=""
ARG VITE_PLAUSIBLE_DOMAIN=""
ARG VITE_PLAUSIBLE_SCRIPT=""
RUN npm run build

FROM nginx:1.30-alpine

# The image's welcome page, never to be served.
RUN rm /etc/nginx/conf.d/default.conf
COPY --from=build /app/web/dist/ /usr/share/nginx/html/

EXPOSE 80 443
