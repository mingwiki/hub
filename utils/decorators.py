import time

from decorator import decorator

from .extra import run_in_executor
from .logging import logger

log = logger(__name__)


@decorator
async def atimer(func, debug=False, sync=False, *args, **kwargs):
    start_time = time.perf_counter()
    result = await run_in_executor(func, *args, **kwargs) if sync else await func(*args, **kwargs)
    log.debug(
        f"{func.__module__}-{func.__name__}{(args, kwargs)} with execution time: {(time.perf_counter() - start_time) * 1000:.2f} ms {f'returns {result}' if debug else ''}"
    )
    return result
