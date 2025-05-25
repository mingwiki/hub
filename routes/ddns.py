import os

import httpx
from fastapi import APIRouter, Depends, Request
from fastapi.responses import PlainTextResponse

from models import Keyring, get_current_user
from schemas import UserResponse
from utils import atimer, generate_key, send_to_bark

router = APIRouter(tags=["Cloudflare DDNS"], prefix="/ddns")


@router.post("/")
@atimer
async def generate_short_link_for_homeserver(
    request: Request,
    current_user: UserResponse = Depends(get_current_user),
):
    if not current_user["is_admin"]:
        return PlainTextResponse("Permission denied.", status_code=403)
    short_link = generate_key(prefix="ddns")
    Keyring.set(
        short_link,
        {
            "username": current_user["username"],
            "ip": request.headers.get("X-Forwarded-For", request.client.host),
        },
    )
    return PlainTextResponse(f"Shortened URL: https://api.zed.ink/ddns/{short_link}")


@router.get("/{short_link}")
@atimer
async def update_cloudflare_dns_for_homeserver_by_currrent_ip(
    request: Request, short_link: str
):
    data = Keyring.get(short_link)
    if not data:
        return PlainTextResponse("Short link data not found.", status_code=404)

    current_ip = request.headers.get("X-Forwarded-For", request.client.host)

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
