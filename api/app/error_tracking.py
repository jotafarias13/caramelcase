"""Error tracking with Better Stack, on only when its DSN is set.

The setting is BETTER_STACK_ERRORS_DSN. Better Stack accepts what the
Sentry SDK sends, so the SDK is Sentry's and only the DSN points at
Better Stack.
"""

import sentry_sdk

from app.settings import Settings


def setup_error_tracking(settings: Settings) -> bool:
    """Send unhandled errors to Better Stack if a DSN is set; say if it did.

    Without a DSN nothing is started and nothing leaves the server.
    """
    if not settings.better_stack_errors_dsn:
        return False
    sentry_sdk.init(
        dsn=settings.better_stack_errors_dsn,
        environment=settings.environment,
        traces_sample_rate=settings.better_stack_traces_sample_rate,
        # No cookies, headers that identify the user, or addresses (LGPD).
        send_default_pii=False,
        # Nor request bodies: a sign-in request carries an email address.
        max_request_body_size="never",
    )
    return True
