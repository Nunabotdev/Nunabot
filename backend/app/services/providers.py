import math
from dataclasses import dataclass, field
from ..config import Config
from ..utils import clamp, safe_div


@dataclass
class Provider:
    """A GPU provider and the raw signals its reputation is computed from.
    The reputation score is always derived from these — never stored — so the
    formula can evolve freely."""
    id: str
    operator: str
    gpus: int
    busy: int = 0
    # uptime: heartbeats seen vs expected
    heartbeats: int = 0
    expected_heartbeats: int = 0
    # reliability: completed vs failed
    completed_jobs: int = 0
    failed_jobs: int = 0
    # speed: running average of actual/estimated runtime (lower is faster)
    speed_samples: int = 0
    speed_ratio_sum: float = 0.0
    # quality: running average of 0..1 output-quality ratings
    quality_samples: int = 0
    quality_sum: float = 0.0
    earnings_sol: float = 0.0

    @property
    def available(self) -> int:
        return max(0, self.gpus - self.busy)

    @property
    def utilization(self) -> float:
        return safe_div(self.busy, self.gpus)

    @property
    def uptime(self) -> float:
        if self.expected_heartbeats == 0:
            return 0.8  # new provider: assume decent until proven
        return clamp(safe_div(self.heartbeats, self.expected_heartbeats), 0.0, 1.0)

    @property
    def reliability(self) -> float:
        total = self.completed_jobs + self.failed_jobs
        if total == 0:
            return 0.7
        return clamp(safe_div(self.completed_jobs, total), 0.0, 1.0)

    @property
    def avg_speed_ratio(self) -> float:
        return safe_div(self.speed_ratio_sum, self.speed_samples, default=1.0)

    @property
    def avg_quality(self) -> float:
        return safe_div(self.quality_sum, self.quality_samples, default=0.7)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "operator": self.operator,
            "gpus": self.gpus,
            "busy": self.busy,
            "available": self.available,
            "utilization": round(self.utilization, 3),
            "uptime": round(self.uptime, 3),
            "reliability": round(self.reliability, 3),
            "avg_speed_ratio": round(self.avg_speed_ratio, 3),
            "avg_quality": round(self.avg_quality, 3),
            "completed_jobs": self.completed_jobs,
            "failed_jobs": self.failed_jobs,
            "earnings_sol": round(self.earnings_sol, 6),
        }


_providers: dict[str, Provider] = {}


class ProviderRegistry:
    """Registers GPU providers and computes their reputation from raw signals."""

    VOLUME_REF = 100.0  # ~100 completed jobs saturates the volume component

    def __init__(self, config=Config):
        self.config = config

    def register(self, operator: str, gpus: int) -> Provider:
        from ..utils import new_id
        if gpus <= 0:
            raise ValueError("gpus must be positive")
        p = Provider(id=new_id("prov"), operator=operator, gpus=gpus)
        _providers[p.id] = p
        return p

    def get(self, provider_id: str) -> Provider:
        p = _providers.get(provider_id)
        if not p:
            raise ValueError(f"provider not found: {provider_id}")
        return p

    def list_all(self) -> list[Provider]:
        return list(_providers.values())

    # --- reputation components (each 0..1) ---
    def _uptime_score(self, p: Provider) -> float:
        return p.uptime

    def _speed_score(self, p: Provider) -> float:
        # ratio <= target → full marks; slower than target decays toward 0
        ratio = p.avg_speed_ratio
        target = self.config.SPEED_TARGET_RATIO
        if ratio <= target:
            return 1.0
        return clamp(target / ratio, 0.0, 1.0)

    def _reliability_score(self, p: Provider) -> float:
        return p.reliability

    def _volume_score(self, p: Provider) -> float:
        return clamp(math.log1p(p.completed_jobs) / math.log1p(self.VOLUME_REF), 0.0, 1.0)

    def _quality_score(self, p: Provider) -> float:
        return clamp(p.avg_quality, 0.0, 1.0)

    def components(self, provider_id: str) -> dict:
        p = self.get(provider_id)
        return {
            "uptime": round(self._uptime_score(p), 4),
            "speed": round(self._speed_score(p), 4),
            "reliability": round(self._reliability_score(p), 4),
            "volume": round(self._volume_score(p), 4),
            "quality": round(self._quality_score(p), 4),
        }

    def reputation(self, provider_id: str) -> int:
        p = self.get(provider_id)
        c = self.config
        composite = (
            c.REP_W_UPTIME * self._uptime_score(p)
            + c.REP_W_SPEED * self._speed_score(p)
            + c.REP_W_RELIABILITY * self._reliability_score(p)
            + c.REP_W_VOLUME * self._volume_score(p)
            + c.REP_W_QUALITY * self._quality_score(p)
        )
        return int(round(clamp(composite, 0.0, 1.0) * c.REP_MAX_SCORE))

    def tier(self, provider_id: str) -> str:
        s = self.reputation(provider_id)
        if s >= 800:
            return "elite"
        if s >= 650:
            return "trusted"
        if s >= 450:
            return "rising"
        return "new"

    def earnings_bonus(self, provider_id: str) -> float:
        frac = self.reputation(provider_id) / self.config.REP_MAX_SCORE
        return frac * self.config.REP_MAX_EARNINGS_BONUS

    def reputation_view(self, provider_id: str) -> dict:
        p = self.get(provider_id)
        return {
            **p.to_dict(),
            "reputation": self.reputation(provider_id),
            "tier": self.tier(provider_id),
            "components": self.components(provider_id),
            "earnings_bonus": round(self.earnings_bonus(provider_id), 4),
        }

    # --- signal updates ---
    def heartbeat(self, provider_id: str, online: bool = True):
        p = self.get(provider_id)
        p.expected_heartbeats += 1
        if online:
            p.heartbeats += 1

    def record_result(self, provider_id: str, success: bool, speed_ratio: float = None,
                      quality: float = None):
        p = self.get(provider_id)
        if success:
            p.completed_jobs += 1
            if speed_ratio is not None:
                p.speed_samples += 1
                p.speed_ratio_sum += speed_ratio
            if quality is not None:
                p.quality_samples += 1
                p.quality_sum += quality
        else:
            p.failed_jobs += 1
