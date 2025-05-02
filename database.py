from fastapi import FastAPI
from tortoise import Tortoise

DATABASE_URL = "sqlite://database/db.sqlite3"

TORTOISE_ORM = {
    "connections": {"default": DATABASE_URL},
    "apps": {
        "models": {
            "models": ["models", "aerich.models"],
            "default_connection": "default",
        },
    },
}


# Initialize the database connection
async def init_db(app: FastAPI):
    # Initialize the connection to the database and create tables
    await Tortoise.init(db_url=DATABASE_URL, modules={"models": ["models"]})
    await Tortoise.generate_schemas()

    # Bind the Tortoise instance to the app for shutdown
    app.add_event_handler("shutdown", Tortoise.close_connections)
