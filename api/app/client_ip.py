"""The network address a request comes from."""

from fastapi import Request


def client_ip(request: Request) -> str:
    """The caller's address. nginx puts the real one in X-Real-IP,
    overwriting whatever the client sent; without nginx in front, it is
    the address of the connection.

    The header is trusted, so the API must only be reachable through
    nginx in production (milestone 8).
    """
    if real_ip := request.headers.get("x-real-ip"):
        return real_ip
    return request.client.host if request.client else "unknown"
