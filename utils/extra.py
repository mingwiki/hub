import asyncio
import os
import random
import string

import httpx

from .logging import logger

log = logger(__name__)


async def run_in_executor(func, *args):
    loop = asyncio.get_event_loop()

    return await loop.run_in_executor(None, func, *args)


def bytes2human(n):
    symbols = ("K", "M", "G", "T", "P", "E", "Z", "Y")
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return f"{value:.1f} {s}B"
    return f"{n} B"


def generate_key(prefix: str, key_length: int = 6):
    return f"{prefix}_" + "".join(
        random.choices(string.ascii_letters + string.digits, k=key_length)
    )


async def send_to_bark(
    url_base: str = os.getenv("BARK_URL"),
    token: str = os.getenv("BARK_TOKEN"),
    title: str = "Notification",
    content: str = "",
    group: str = "uncategorized",
    icon: str = "https://static.zed.ink/wiki.png",
):
    url = f"{url_base}/{token}/{title}/{content}?group={group}&icon={icon}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()
