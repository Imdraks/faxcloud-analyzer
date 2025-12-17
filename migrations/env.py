import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlmodel import SQLModel

from app.db.models import Report, ReportRun, Transmission  # noqa: F401
from app.db.session import get_engine_url, init_async_engine

config = context.config
fileConfig(config.config_file_name)  # type: ignore[arg-type]

target_metadata = SQLModel.metadata


def run_migrations_offline():
    url = get_engine_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    engine = init_async_engine()
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
