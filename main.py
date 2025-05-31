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
app.mount("/public", StaticFiles(directory="public"), name="public")
for router in routers:
    app.include_router(router)
