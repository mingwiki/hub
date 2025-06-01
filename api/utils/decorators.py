import time

from decorator import decorator

from .logging import logger

log = logger(__name__)


@decorator
async def atimer(func, *args, **kwargs):
    start_time = time.perf_counter()
    result = await func(*args, **kwargs)
    log.debug(
        f"{func.__module__}-{func.__name__}{(args, kwargs)} return {result} with {(time.perf_counter() - start_time) * 1000:.3f} ms"
    )
    return result
