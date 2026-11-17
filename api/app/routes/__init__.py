"""The routes of the API, one module per area, all under /api/v1.

A route reads its input, calls a service, commits and returns a model
from app/schemas/. dependencies.py has what they share: the signed-in
user, the CSRF header and feature flags.
"""
