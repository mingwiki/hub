from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from routes import routers

try:
    import uvloop
except ImportError:
    pass
else:
    uvloop.install()


api = FastAPI(
    title="API Service",
    version="0.0.1",
    swagger_ui_parameters={"displayRequestDuration": True, "tryItOutEnabled": True},
)

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
for router in routers:
    api.include_router(router)

app = FastAPI(title="main")
app.mount("/api", api, name="api")
app.mount("/", StaticFiles(directory="static", html=True), name="web")
