import os

import httpx
from fastapi import APIRouter, Depends, Request
from fastapi.responses import PlainTextResponse

from models import KeyringHandler, User, get_current_user
from utils import atimer, generate_key, logger, send_to_bark

router = APIRouter(tags=["Cloudflare DDNS"], prefix="/ddns")
log = logger(__name__)
keyring = KeyringHandler()


@router.post("/")
@atimer(debug=True)
async def generate_short_link_for_homeserver(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    if current_user.username != "mingwiki":
        return PlainTextResponse("Permission denied.", status_code=403)
    short_link = generate_key(prefix="ddns")
    await keyring.set(
        short_link,
        {
            "username": current_user.username,
            "headers": dict(request.headers),
            "client": request.client.host,
        },
    )
    return PlainTextResponse(f"Shortened URL: https://api.zed.ink/ddns/{short_link}")


@router.get("/client_info")
@atimer(debug=True)
async def client_info(request: Request):
    return {"client": request.client, "headers": dict(request.headers)}


@router.get("/{short_link}")
@atimer(debug=True)
async def update_cloudflare_dns_for_homeserver_by_currrent_ip(
    request: Request, short_link: str
):
    data = await keyring.get(short_link)
    if not data:
        log.debug(f"Short link data not found, short_link is: {short_link}")
        return PlainTextResponse("Short link data not found.", status_code=404)

    current_ip = request.headers.get("X-Forwarded-For", request.client.host)
    log.debug(
        f"Updating DNS record for home server with IP: {current_ip} and token: {current_ip}"
    )
    headers = {
        "Authorization": f"Bearer {os.getenv('CLOUDFLARE_API_TOKEN')}",
        "Content-Type": "application/json",
    }
    data = {"type": "A", "name": "home.zed.ink", "content": current_ip, "ttl": 1}
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"https://api.cloudflare.com/client/v4/zones/{os.getenv("CLOUDFLARE_ZONE_ID")}/dns_records/{os.getenv("CLOUDFLARE_HOME_RECORD_ID")}",
            json=data,
            headers=headers,
        )
    return {
        "cloudflare_ddns": response.json(),
        "bark": await send_to_bark(
            title="DDNS Update",
            content=f"IP: {current_ip} 更新成功",
            group="DDNS",
        ),
    }
