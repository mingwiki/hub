import os

import httpx


async def send_to_bark(
    url_base: str = "https://bark.zed.ink",
    token: str = os.getenv("BARK_TOKEN"),
    title: str = "服务器快照",
    content: str = "",
    group: str = "Snapshot",
    icon: str = "https://static.zed.ink/wiki.png",
):
    url = f"{url_base}/{token}/{title}/{content}?group={group}&icon={icon}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()
