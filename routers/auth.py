import aiohttp
from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import RedirectResponse

from config import Config
from utils import logger

router = APIRouter(tags=["Authorization"])
log = logger(__name__)


@router.get("/login")
async def login():
    oauth_data = await Config.get_gitea_oauth()
    return RedirectResponse(
        f"{oauth_data['authorize_url']}?client_id={oauth_data['client_id']}&redirect_uri=https://api.zed.ink/auth/callback&response_type=code"
    )


@router.get("/auth/callback")
async def auth_callback(code: str):
    oauth_data = await Config.get_gitea_oauth()
    async with aiohttp.ClientSession() as session:
        async with session.post(
            oauth_data["token_url"],
            data={
                "client_id": oauth_data["client_id"],
                "client_secret": oauth_data["client_secret"],
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": "https://api.zed.ink/auth/callback",
            },
            headers={"Accept": "application/json"},
        ) as response:
            if response.status != 200:
                raise HTTPException(
                    status_code=response.status,
                    detail="Failed to get token, visit: https://api.zed.ink/login ",
                )
            return await response.json()


@router.get("/me")
async def get_user_info(x_token: str | None = Header(default=None)):
    oauth_data = await Config.get_gitea_oauth()
    async with aiohttp.ClientSession() as session:
        async with session.get(
            oauth_data["user_url"], headers={"Authorization": f"Bearer {x_token}"}
        ) as response:
            if response.status != 200:
                raise HTTPException(
                    status_code=response.status,
                    detail="Failed to get user info, visit: https://api.zed.ink/login ",
                )
            return await response.json()
