"""Database: the engine and session, the models and their migrations.

- session.py     the engine and the per-request session
- base.py        the base class and the conventions every table follows
- models/        every table, one module per area of the data model
- migrations/    Alembic: env.py and one file per schema change
"""
