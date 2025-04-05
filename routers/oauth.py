import httpx
from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import RedirectResponse

from models import get_config
from utils import logger

router = APIRouter(tags=["GitHub OAuth"], prefix="/oauth")
log = logger(__name__)


@router.get("/login")
async def login():
    oauth_data = await get_config("github_oauth")
    return RedirectResponse(
        f"{oauth_data['authorize_url']}?client_id={oauth_data['client_id']}&redirect_uri=https://api.zed.ink/oauth/callback&response_type=code"
    )


@router.get("/callback")
async def auth_callback(code: str):
    oauth_data = await get_config("github_oauth")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            oauth_data["token_url"],
            data={
                "client_id": oauth_data["client_id"],
                "client_secret": oauth_data["client_secret"],
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": "https://api.zed.ink/oauth/callback",
            },
            headers={"Accept": "application/json"},
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail="Failed to get token, visit: https://api.zed.ink/oauth/login ",
            )
        return response.json()


@router.get("/me")
async def get_user_info(x_token: str | None = Header(default=None)):
    oauth_data = await get_config("github_oauth")
    async with httpx.AsyncClient() as client:
        response = await client.get(oauth_data["user_url"], headers={"Authorization": f"Bearer {x_token}"})
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail="Failed to get user info, visit: https://api.zed.ink/oauth/login ",
            )
        return response.json()
