import base64

from .decorators import atimer


@atimer(debug=True, sync=True)
def decode(b64_url: str):
    b64_url = b64_url.replace("-", "+").replace("_", "/")
    b64_url += "=" * (-len(b64_url) % 4)
    return base64.b64decode(b64_url).decode("utf-8")


@atimer(debug=True, sync=True)
def encode(url: str):
    return base64.b64encode(url.encode()).decode()
