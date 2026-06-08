from ..config import Config
from ..utils import clamp


class JobRouter:
    """Picks which provider runs a job. Routing score blends reputation with
    free capacity: high-rep providers win, but only if they have a GPU free, and
    spare capacity breaks ties so the network load-balances."""

    def __init__(self, providers, config=Config):
        self.providers = providers
        self.config = config

    def _routing_score(self, provider) -> float:
        rep_frac = self.providers.reputation(provider.id) / self.config.REP_MAX_SCORE
        capacity_frac = clamp(provider.available / max(1, provider.gpus), 0.0, 1.0)
        w = self.config.ROUTING_REP_WEIGHT
        return w * rep_frac + (1.0 - w) * capacity_frac

    def candidates(self) -> list:
        return [p for p in self.providers.list_all() if p.available > 0]

    def pick(self):
        avail = self.candidates()
        if not avail:
            raise ValueError("no providers with free capacity")
        return max(avail, key=self._routing_score)

    def ranked(self) -> list:
        return sorted(self.candidates(), key=self._routing_score, reverse=True)
