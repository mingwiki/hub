import os

from piccolo.conf.apps import AppRegistry
from piccolo.engine.postgres import PostgresEngine
from piccolo.engine.sqlite import SQLiteEngine

# Determine the environment
ENV = os.environ.get("ENV", "dev").lower()

# Configure database based on environment
if ENV == "prod":
    # Production PostgreSQL configuration
    DB = PostgresEngine(
        config={
            "database": os.environ.get("DB_NAME", "core"),
            "user": os.environ.get("DB_USER", "core"),
            "password": os.environ.get("DB_PASSWORD", "core"),
            "host": os.environ.get("DB_HOST", "localhost"),
            "port": int(os.environ.get("DB_PORT", 5432)),
        }
    )
else:
    # Development SQLite configuration
    DB = SQLiteEngine(
        path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "core.dev.db")
    )

# App registry remains the same
APP_REGISTRY = AppRegistry(apps=[])
