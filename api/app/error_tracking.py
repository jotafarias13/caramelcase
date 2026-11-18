"""Error tracking with Sentry, switched on only when SENTRY_DSN is set."""

import sentry_sdk

from app.settings import Settings


def setup_error_tracking(settings: Settings) -> bool:
    """Send unhandled errors to Sentry if a DSN is set; say whether it did.

    Without a DSN nothing is started and nothing leaves the server.
    """
    if not settings.sentry_dsn:
        return False
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.environment,
        traces_sample_rate=settings.sentry_traces_sample_rate,
        # No cookies, headers that identify the user, or addresses (LGPD).
        send_default_pii=False,
        # Nor request bodies: a sign-in request carries an email address.
        max_request_body_size="never",
    )
    return True
