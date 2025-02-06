import asyncio

import uvloop
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models.db import create_tables
from routers import auth, ddns, public, swas, webhooks
from utils import close_http_client

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

app = FastAPI(
    title="API Service",
    version="0.0.1",
    contact={"email": "mingwiki@gmail.com"},
    docs_url="/",
    swagger_ui_parameters={"displayRequestDuration": True, "tryItOutEnabled": True},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(ddns.router)
app.include_router(public.router)
app.include_router(webhooks.router)
app.include_router(swas.router)


@app.on_event("startup")
async def startup():
    await create_tables()


@app.on_event("shutdown")
async def shutdown_event():
    await close_http_client()
