from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
from routers import auth

try:
    import uvloop
except ImportError:
    pass
else:
    uvloop.install()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db(app=app)
    yield


app = FastAPI(
    title="API Service",
    version="0.0.1",
    contact={"email": "mingwiki@gmail.com"},
    docs_url="/",
    swagger_ui_parameters={"displayRequestDuration": True, "tryItOutEnabled": True},
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)
