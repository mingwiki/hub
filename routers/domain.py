from fastapi import Form, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from models import DomainTreeManager

templates = Jinja2Templates(directory="templates")

from fastapi import APIRouter, Request

router = APIRouter(tags=["Proxy file"], prefix="/domain")
mgr = DomainTreeManager()


@router.get("/", response_class=HTMLResponse)
async def form_view(request: Request):
    return templates.TemplateResponse(
        "domain.html", {"request": request, "domains": mgr.list_full_domains()}
    )


@router.post("/submit/")
async def submit(adds: str = Form(""), dels: str = Form("")):
    add_list = [l for l in adds.splitlines() if l.strip()]
    del_list = [l for l in dels.splitlines() if l.strip()]
    mgr.batch(add_list, del_list)
    return RedirectResponse("/domain", status_code=303)


@router.post("/import_rules")
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

    return RedirectResponse(url="/domain", status_code=303)


@router.get("/pac")
async def autoproxy_pac():
    """
    Generate a PAC file routing all listed domains DIRECTLY,
    and sending everything else via proxy:8080.
    """
    domains = mgr.list_full_domains()
    # Build if-clauses for each domain
    lines = []
    for d in domains:
        # match exact host or any subdomain
        lines.append(
            f'    if (shExpMatch(host, "*.{d}") || host == "{d}") return "proxy";'
        )
    body = "\n".join(lines)
    pac = f"""
function FindProxyForURL(url, host) {{
{body}
    return "PROXY proxy.example.com:8080; DIRECT";
}}
"""
    return Response(pac.strip(), media_type="application/x-ns-proxy-autoconfig")


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


@router.get("/list")
async def autoproxy_txt():

    return Response(get_autoproxy_txt(), media_type="text/plain")


@router.get("/b64")
async def autoproxy_base64():
    import base64

    return Response(
        base64.b64encode(get_autoproxy_txt().encode()).decode(), media_type="text/plain"
    )
