"""gunicorn's settings for production (deploy/api.Dockerfile).

    gunicorn -c gunicorn.conf.py

Uvicorn workers run the FastAPI app. Every line is written through loguru
(app/logger.py), so gunicorn's own lines are JSON like the app's.
"""

from app.logger import setup_logging
from app.settings import get_settings

settings = get_settings()
setup_logging()

wsgi_app = "app.main:app"
worker_class = "uvicorn_worker.UvicornWorker"
workers = settings.gunicorn_workers
# Reached only through nginx, on the compose network
# (deploy/docker-compose.yml publishes no port).
bind = "0.0.0.0:8000"
timeout = settings.gunicorn_timeout_seconds
# gunicorn 27's control socket (for gunicornc) is not used, and the image's
# user has no home directory to put it in.
control_socket_disable = True
# The app logs every request itself (app/logger.py, log_request).
accesslog = None
loglevel = settings.log_level.lower()
# gunicorn's own lines go to loguru. Each worker hands uvicorn's loggers
# the handlers of gunicorn.error, so they arrive there too.
logconfig_dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"loguru": {"class": "app.logger.InterceptHandler"}},
    "root": {"level": settings.log_level, "handlers": ["loguru"]},
    "loggers": {
        "gunicorn.error": {
            "level": settings.log_level,
            "handlers": ["loguru"],
            "propagate": False,
        },
        "gunicorn.access": {
            "level": "INFO",
            "handlers": ["loguru"],
            "propagate": False,
        },
    },
}
