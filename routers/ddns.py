import httpx
from decorator import decorator
from robyn import Request, Response, SubRouter

from models import CacheDB, get_config
from routers.auth import get_user_info
from utils import atimer, logger

router = SubRouter(__file__, prefix="/ddns")
log = logger(__name__)


@decorator
async def is_authorized(func, request: Request, *args, **kwargs):
    x_token = request.headers.get("x-token")
    if not x_token:
        return Response(status_code=401, description="Missing x-token header.")

    user_info = await get_user_info(x_token)
    if user_info["login"] != "mingwiki":
        return Response(status_code=403, description="You are not authorized to update the DNS record.")

    return await func(request, *args, **kwargs)


@router.post("/")
@is_authorized
@atimer(debug=True)
async def generate_short_link_for_homeserver(request: Request):
    x_token = request.headers.get("x-token")
    cache = CacheDB()
    short_link = await cache.save_short_link_data(x_token)
    return Response(status_code=200, description=f"Shortened URL: https://api.zed.ink/ddns/{short_link}")


@router.get("/{short_link}")
@atimer(debug=True)
async def update_cloudflare_dns_for_homeserver_by_currrent_ip(request: Request, short_link: str):
    cache = CacheDB()
    data = await cache.get_short_link_data(short_link)
    if not data:
        log.debug(f"Short link data not found, short_link is: {short_link}")
        return Response(status_code=404, description="Short link data not found.")

    return await update_cloudflare_dns_for_homeserver(request, x_token=data, x_ip=request.ip_addr)


@router.put("/")
@is_authorized
@atimer(debug=True)
async def update_cloudflare_dns_for_homeserver(request: Request):
    x_token = request.headers.get("x-token")
    x_ip = request.headers.get("x-ip")
    if not x_ip:
        return Response(status_code=400, description="Missing x-ip header.")

    cloudflare_ddns = await get_config("cloudflare_ddns")
    log.debug(f"Updating DNS record for home server with IP: {x_ip} and token: {x_token}")

    headers = {
        "Authorization": f"Bearer {cloudflare_ddns['api_token']}",
        "Content-Type": "application/json",
    }
    data = {"type": "A", "name": "home.zed.ink", "content": x_ip, "ttl": 1}

    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"https://api.cloudflare.com/client/v4/zones/{cloudflare_ddns['zone_id']}/dns_records/{cloudflare_ddns['record_id']}",
            json=data,
            headers=headers,
        )
        return Response(status_code=response.status_code, description=response.json())
