import time
import threading


class RateLimiter:
    """Token-bucket limiter. Thread-safe, refills continuously."""

    def __init__(self, rate: float, capacity: int):
        self.rate = rate
        self.capacity = capacity
        self._tokens = float(capacity)
        self._last = time.monotonic()
        self._lock = threading.Lock()

    def allow(self, cost: float = 1.0) -> bool:
        with self._lock:
            now = time.monotonic()
            self._tokens = min(self.capacity, self._tokens + (now - self._last) * self.rate)
            self._last = now
            if self._tokens >= cost:
                self._tokens -= cost
                return True
            return False


class SlidingWindowLimiter:
    """Fixed number of events allowed per rolling window (seconds)."""

    def __init__(self, max_events: int, window: float):
        self.max_events = max_events
        self.window = window
        self._events: dict[str, list[float]] = {}
        self._lock = threading.Lock()

    def allow(self, key: str = "global") -> bool:
        now = time.monotonic()
        with self._lock:
            hits = [t for t in self._events.get(key, []) if now - t < self.window]
            if len(hits) >= self.max_events:
                self._events[key] = hits
                return False
            hits.append(now)
            self._events[key] = hits
            return True
