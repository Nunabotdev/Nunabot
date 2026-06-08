import time
import asyncio
import functools
from .logger import get_logger

log = get_logger("retry")


def retry(times: int = 3, delay: float = 0.5, backoff: float = 2.0, exceptions=(Exception,)):
    """Retry decorator for sync and async callables with exponential backoff."""

    def decorator(fn):
        if asyncio.iscoroutinefunction(fn):
            @functools.wraps(fn)
            async def awrapper(*args, **kwargs):
                wait = delay
                last = None
                for attempt in range(1, times + 1):
                    try:
                        return await fn(*args, **kwargs)
                    except exceptions as e:  # noqa: PERF203
                        last = e
                        if attempt == times:
                            break
                        log.warning("%s failed (attempt %d/%d): %s", fn.__name__, attempt, times, e)
                        await asyncio.sleep(wait)
                        wait *= backoff
                raise last
            return awrapper

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            wait = delay
            last = None
            for attempt in range(1, times + 1):
                try:
                    return fn(*args, **kwargs)
                except exceptions as e:  # noqa: PERF203
                    last = e
                    if attempt == times:
                        break
                    log.warning("%s failed (attempt %d/%d): %s", fn.__name__, attempt, times, e)
                    time.sleep(wait)
                    wait *= backoff
            raise last
        return wrapper
    return decorator
