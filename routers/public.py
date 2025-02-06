import io
from datetime import datetime
from functools import lru_cache

import aiohttp
import matplotlib.pyplot as plt
from fake_useragent import UserAgent
from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import StreamingResponse
from yarl import URL

from models.db import SqliteCache
from utils import atimer, decode, get_http_client, logger

log = logger(__name__)
router = APIRouter(tags=["公共服务"])
api_up_time = datetime.now()


@lru_cache
def generate_status_code_image(status_code: int):
    fig, ax = plt.subplots(figsize=(2, 2))
    ax.set_facecolor("white")
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, color="white", ec="black", lw=5))
    ax.text(
        0.5, 0.5, str(status_code), color="red", fontsize=20, ha="center", va="center"
    )
    ax.axis("off")
    img_byte_array = io.BytesIO()
    plt.savefig(img_byte_array, format="png", dpi=100)
    img_byte_array.seek(0)
    plt.close(fig)
    return img_byte_array.getvalue()


async def stream_content(url: str, session: aiohttp.ClientSession):
    cache = SqliteCache()
    cache_key = f"media_cache:{url}"
    cached_content = await cache.get(cache_key)

    def is_unstreamable_type(content_type):
        return content_type.startswith("text") or "image/svg+xml" in content_type

    if cached_content:
        if (
            isinstance(cached_content, dict)
            and "type" in cached_content
            and "content" in cached_content
        ):
            content_type = cached_content["type"]
            content = cached_content["content"]

            if is_unstreamable_type(content_type):
                yield content
            else:
                for chunk in content:
                    yield chunk
            return
        log.error(f"Cached content for {url} is invalid")
        await cache.delete(cache_key)
    async with session.get(
        url,
        headers={"User-Agent": UserAgent().random, "Connection": "keep-alive"},
        allow_redirects=True,
        timeout=aiohttp.ClientTimeout(total=120),
    ) as response:
        if response.status != 200:
            log.warning(
                f"Request failed for {url}, headers: {response.headers}, status: {response.status}"
            )
            yield generate_status_code_image(response.status)
            return

        content_type = response.headers.get("Content-Type", "application/octet-stream")

        if is_unstreamable_type(content_type):
            content = await response.read()
            await cache.set(cache_key, {"content": content, "type": content_type})
            yield content
        else:
            chunks = []
            async for chunk in response.content.iter_chunked(8192):
                yield chunk
                chunks.append(chunk)
            await cache.set(cache_key, {"content": chunks, "type": content_type})


@router.get("/media/{b64_url:path}")
async def media_proxy(
    decode_url: str = Depends(decode),
    session: aiohttp.ClientSession = Depends(get_http_client),
):
    try:
        url = URL(decode_url)
    except Exception as e:
        log.error(f"Invalid URL: {decode_url} with exception: {str(e)}")
        return Response(content=generate_status_code_image(400), media_type="image/png")

    return StreamingResponse(stream_content(str(url), session))


@router.delete("/cache")
@router.delete("/cache/{key:path}")
@atimer(debug=True)
async def clean_cache_items(key: str = "", days: int = 30):
    cache = SqliteCache()
    if key:
        return await cache.delete(key)
    return await cache.delete_x_days_ago_old_items(days)


@router.get("/client_info")
async def get_client_info(request: Request):
    return {
        "client": request.client,
        "headers": request.headers,
        "query_params": request.query_params,
        "path_params": request.path_params,
        "cookies": request.cookies,
        "url_for": request.url_for,
        "base_url": request.base_url,
        "url": request.url,
        "method": request.method,
    }
