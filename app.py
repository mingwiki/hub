from robyn import Robyn

from models import db
from routers import auth, ddns, swas, webhooks

app = Robyn(__file__)


@app.startup_handler
async def startup_handler() -> None:
    await db.connect()


@app.shutdown_handler
async def shutdown_handler() -> None:
    if db.is_connected():
        await db.disconnect()


app.include_router(auth.router)
app.include_router(ddns.router)
app.include_router(swas.router)
app.include_router(webhooks.router)

app.start(port=9999, host="0.0.0.0")
