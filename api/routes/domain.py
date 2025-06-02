from fastapi import APIRouter, Form, Response
from fastapi.responses import RedirectResponse
from services import DomainTreeManager
from utils import atimer, logger

router = APIRouter(tags=["Domain Manage"], prefix="/domain")
mgr = DomainTreeManager()
log = logger(__name__)


@router.get("/")
@atimer
async def list_domains():
    return mgr.list_full_domains()


@router.post("/")
@atimer
async def submit(adds: str = Form(""), dels: str = Form("")):
    add_list = [l for l in adds.splitlines() if l.strip()]
    del_list = [l for l in dels.splitlines() if l.strip()]
    mgr.batch(add_list, del_list)
    return RedirectResponse("/#domain", status_code=303)


@router.post("/import")
@atimer
async def import_rules(rules: str = Form(...)):
    domains = []
    for line in rules.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if not parts:
            continue
        domain = parts[0].lstrip("*.")  # Remove leading "*." if present
        domains.append(domain)

    if domains:
        mgr.batch(domains, [])  # Add only

    return RedirectResponse(url="/#domain", status_code=303)


def get_autoproxy_txt():
    """
    Returns the current tree as an Autoproxy list:
      ||domain.tld
      ||sub.domain.tld
    """
    # get your full hostnames
    domains = mgr.list_full_domains()
    # build Autoproxy lines
    lines = ["[AutoProxy]"]
    lines += [f"||{d}" for d in domains]
    body = "\n".join(lines)
    return body


@router.get("/b64")
@atimer
async def autoproxy_base64():
    import base64

    return Response(
        base64.b64encode(get_autoproxy_txt().encode()).decode(), media_type="text/plain"
    )
