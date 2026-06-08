import httpx
from ..config import Config
from ..utils import get_logger, TTLCache, retry

log = get_logger("solana")


class SolanaClient:
    """Minimal SOL/USD price oracle with a deterministic fallback so dev and
    tests run with no network or keys."""

    FALLBACK_SOL_USD = 150.0

    def __init__(self, config=Config):
        self.config = config
        self._cache = TTLCache(ttl=config.PRICE_CACHE_TTL)

    def sol_price_usd(self) -> float:
        cached = self._cache.get("sol_usd")
        if cached is not None:
            return cached
        price = self._fetch()
        self._cache.set("sol_usd", price)
        return price

    @retry(times=2, delay=0.3, exceptions=(httpx.HTTPError,))
    def _fetch(self) -> float:
        try:
            url = f"{self.config.PRICE_API}/simple/price"
            r = httpx.get(url, params={"ids": "solana", "vs_currencies": "usd"}, timeout=5.0)
            r.raise_for_status()
            return float(r.json()["solana"]["usd"])
        except Exception as e:  # noqa: BLE001
            log.warning("SOL price fetch failed, using fallback: %s", e)
            return self.FALLBACK_SOL_USD
