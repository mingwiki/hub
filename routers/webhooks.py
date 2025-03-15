import json

import aiohttp
from fastapi import APIRouter, Header, Request

from models.db import WebhooksDB, get_config
from utils import atimer, logger, send_to_bark

log = logger(__name__)
router = APIRouter(tags=["Webhooks"], prefix="/hooks")


@router.post("/flux")
@atimer(debug=True)
async def miniflux_rss(request: Request):
    res = await request.json()

    if "feed" not in res:
        return

    data = {"entries": res["entries"], "title": res["feed"]["title"]}

    key = await WebhooksDB.save_entry(data)
    log.info(f"Webhook data stored: {key}")

    return {"message": "Data saved", "key": key}


@router.post("/flux/send")
@atimer(debug=True)
async def send_summary(name: str | None = Header(default=None)):
    if name is None:
        return "No Bark configuration name provided"

    unsent_entries = await WebhooksDB.get_unsent_entries()

    total_unsent_entries = 0

    for entry in unsent_entries:
        data = entry.get("data") if isinstance(entry, dict) else json.loads(entry).get("data", {})
        data = json.loads(data) if not isinstance(data, dict) else data
        total_unsent_entries += len(data.get("entries", []))

    miniflux = await get_config("miniflux")
    bark = await get_config("bark")
    async with aiohttp.ClientSession() as session:
        headers = {"X-Auth-Token": miniflux["token"]}
        async with session.get(f"{miniflux['url']}entries?status=unread&direction=desc", headers=headers) as response:
            if response.status != 200:
                return f"Failed to fetch unread entries from Miniflux: {response.status}"
            unread_entries = await response.json()

        result = await send_to_bark(
            token=bark[name],
            title="RSS汇总",
            content=f"已更新{total_unsent_entries}条，剩余{unread_entries['total']}条未读",
            group="RSS",
        )

        for entry in unsent_entries:
            await WebhooksDB.mark_as_sent(entry["key"])

        return result
