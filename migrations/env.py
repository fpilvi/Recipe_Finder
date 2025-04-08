from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from alembic.config import Config
import os
from dotenv import load_dotenv

load_dotenv()

config = Config(os.path.join(os.path.dirname(__file__), "..", "alembic.ini"))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from app.models import Base
target_metadata = Base.metadata

database_url = os.getenv("DATABASE_URL")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        {
            "sqlalchemy.url": database_url
        },
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


def run_migrations():
    """Run migrations based on the mode."""
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        run_migrations_online()


if __name__ == "__main__":
    run_migrations()
