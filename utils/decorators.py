import time

import httpx
from decorator import decorator
from fastapi import HTTPException
from fastapi.responses import PlainTextResponse

from .extra import run_in_executor
from .logging import logger

log = logger(__name__)


@decorator
async def atimer(func, debug=False, sync=False, *args, **kwargs):
    start_time = time.perf_counter()
    result = await run_in_executor(func, *args, **kwargs) if sync else await func(*args, **kwargs)
    log.debug(
        f"{func.__module__}-{func.__name__}{(args, kwargs)} with execution time: {(time.perf_counter() - start_time) * 1000:.2f} ms {f'returns {result}' if debug else ''}"
    )
    return result


@decorator
async def is_authorized(func, token, *args, **kwargs):
    async with httpx.AsyncClient() as client:
        response = await client.post("https://api.zed.ink/me", headers={"Authorization": f"Bearer {token}"})
        if response.status_code != 200:
            return PlainTextResponse("Token is invalid or expired.", status_code=401)
        user_info = response.json()
        if user_info["username"] != "mingwiki":
            raise HTTPException(
                status_code=403,
                detail="You are not authorized to perform this action.",
            )
        return await func(token, *args, **kwargs)
