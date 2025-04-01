import asyncio
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


def generate_key(key_length: int = 6):
    return "".join(random.choices(string.ascii_letters + string.digits, k=key_length))


async def send_to_bark(
    token: str = "",
    title: str = "Notification",
    content: str = "",
    group: str = "uncategorized",
    url_base: str = "https://bark.api.zed.ink",
    icon: str = "https://secure.gravatar.com/avatar/50397ee82c4b68806141f68a20fe2e8a",
):
    url = f"{url_base}/{token}/{title}/{content}?group={group}&icon={icon}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()
