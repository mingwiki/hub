import httpx
from robyn import Response, SubRouter

from models import get_config
from utils import logger

router = SubRouter(__file__)
log = logger(__name__)


@router.get("/login")
async def login():
    oauth_data = await get_config("github_oauth")
    redirect_url = f"{oauth_data['authorize_url']}?client_id={oauth_data['client_id']}&redirect_uri=https://api.zed.ink/auth/callback&response_type=code"
    return Response(status_code=302, headers={"Location": redirect_url}, description="Redirecting to GitHub for authentication.")


@router.get("/auth/callback")
async def auth_callback(query_params):
    code = query_params.get("code")
    if not code:
        return Response(status_code=400, description={"detail": "Missing code parameter"})

    oauth_data = await get_config("github_oauth")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            oauth_data["token_url"],
            data={
                "client_id": oauth_data["client_id"],
                "client_secret": oauth_data["client_secret"],
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": "https://api.zed.ink/auth/callback",
            },
            headers={"Accept": "application/json"},
        )
        if response.status_code != 200:
            return Response(
                status_code=response.status_code,
                description={"detail": "Failed to get token, visit: https://api.zed.ink/login"},
            )
        return Response(status_code=200, description=response.json())


@router.get("/me")
async def get_user_info(headers):
    x_token = headers.get("x-token")
    if not x_token:
        return Response(status_code=401, description={"detail": "Missing x-token header"})

    oauth_data = await get_config("github_oauth")
    async with httpx.AsyncClient() as client:
        response = await client.get(oauth_data["user_url"], headers={"Authorization": f"Bearer {x_token}"})
        if response.status_code != 200:
            return Response(
                status_code=response.status_code,
                description={"detail": "Failed to get user info, visit: https://api.zed.ink/login"},
            )
        return Response(status_code=200, description=response.json())
