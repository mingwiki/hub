from .ddns import router as ddns_router
from .domain import router as domain_router
from .user import router as user_router

routers = [ddns_router, domain_router, user_router]
