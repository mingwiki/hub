from tortoise import Tortoise

DATABASE_URL = "sqlite://db.sqlite3"

TORTOISE_ORM = {
    "connections": {"sqlite": DATABASE_URL},
    "apps": {
        "models": {
            "models": ["models", "aerich.models"],
            "default_connection": "sqlite",
        },
    },
}


async def init_db():
    await Tortoise.init(db_url=DATABASE_URL, modules={"models": ["models"]})
    await Tortoise.generate_schemas()


async def close_db():
    await Tortoise.close_connections()
