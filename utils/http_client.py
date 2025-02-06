import aiohttp

_shared_session = None


async def get_http_client():
    global _shared_session
    if _shared_session is None or _shared_session.closed:
        _shared_session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(verify_ssl=False)
        )
    return _shared_session


async def close_http_client():
    global _shared_session
    if _shared_session and not _shared_session.closed:
        await _shared_session.close()
