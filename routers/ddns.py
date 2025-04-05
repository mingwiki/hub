import httpx
from fastapi import APIRouter, Header, Request
from fastapi.responses import PlainTextResponse

from models import CacheDB, get_config
from utils import atimer, is_authorized, logger

router = APIRouter(tags=["DDNS"], prefix="/ddns")
log = logger(__name__)


@router.post("/")
@is_authorized
@atimer(debug=True)
async def generate_short_link_for_homeserver(
    token: str | None = Header(default=None),
):
    cache = CacheDB()
    short_link = await cache.save_data_as_short_link(token)
    return PlainTextResponse(f"Shortened URL: https://api.zed.ink/ddns/{short_link}")


@router.get("/{short_link}")
@atimer(debug=True)
async def update_cloudflare_dns_for_homeserver_by_currrent_ip(request: Request, short_link: str):
    cache = CacheDB()
    data = await cache.get_data_from_short_link(short_link)
    if not data:
        log.debug(f"Short link data not found, short_link is: {short_link}")
        return PlainTextResponse("Short link data not found.", status_code=404)

    return await update_cloudflare_dns_for_homeserver(token=data, x_ip=request.client.host)


@router.put("/")
@is_authorized
@atimer(debug=True)
async def update_cloudflare_dns_for_homeserver(token: str = Header(), x_ip: str = Header()):
    cloudflare_ddns = await get_config("cloudflare_ddns")
    log.debug(f"Updating DNS record for home server with IP: {x_ip} and token: {token}")
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
        return response.json()
