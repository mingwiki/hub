import json

import httpx
from robyn import Request, Response, SubRouter

from models import WebhooksDB, get_config
from utils import atimer, logger, send_to_bark

log = logger(__name__)
router = SubRouter(__file__)


@router.get("/hooks/flux")
@atimer(debug=True)
async def miniflux_rss(request: Request):
    res = await request.json()

    if "feed" not in res:
        return Response(status_code=400, description={"error": "Invalid payload"})

    data = {"entries": res["entries"], "title": res["feed"]["title"]}

    key = await WebhooksDB.save_entry(data)
    log.info(f"Webhook data stored: {key}")

    return Response(status_code=200, description={"message": "Data saved", "key": key})


@router.post("/hooks/flux/send")
@atimer(debug=True)
async def send_summary(request: Request):
    name = request.headers.get("name")
    if name is None:
        return Response(status_code=400, description={"error": "No Bark configuration name provided"})

    unsent_entries = await WebhooksDB.get_unsent_entries()

    total_unsent_entries = 0

    for entry in unsent_entries:
        data = entry.get("data") if isinstance(entry, dict) else json.loads(entry).get("data", {})
        data = json.loads(data) if not isinstance(data, dict) else data
        total_unsent_entries += len(data.get("entries", []))

    miniflux = await get_config("miniflux")
    bark = await get_config("bark")
    async with httpx.AsyncClient() as client:
        headers = {"X-Auth-Token": miniflux["token"]}
        response = await client.get(f"{miniflux['url']}entries?status=unread&direction=desc", headers=headers)
        if response.status_code != 200:
            return Response(
                status_code=500,
                description={"error": f"Failed to fetch unread entries from Miniflux: {response.status_code}"},
            )
        unread_entries = response.json()

        result = await send_to_bark(
            token=bark[name],
            title="RSS汇总",
            content=f"已更新{total_unsent_entries}条，剩余{unread_entries['total']}条未读",
            group="RSS",
        )

        for entry in unsent_entries:
            await WebhooksDB.mark_as_sent(entry["key"])

        return Response(status_code=200, description=result)
