from dataclasses import dataclass, field
from ..config import Config
from ..utils import get_logger, new_id, safe_div, bps, utcnow_iso

log = get_logger("jobs")


@dataclass
class Job:
    id: str
    requester: str
    task_key: str
    units_multiple: float
    provider_id: str
    est_seconds: float
    sol_cost: float
    fee_sol: float
    status: str               # running | completed | failed
    created_at: str
    actual_seconds: float = None
    quality: float = None
    provider_earned_sol: float = 0.0
    closed_at: str = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "requester": self.requester,
            "task_key": self.task_key,
            "units_multiple": self.units_multiple,
            "provider_id": self.provider_id,
            "est_seconds": self.est_seconds,
            "sol_cost": round(self.sol_cost, 6),
            "fee_sol": round(self.fee_sol, 6),
            "status": self.status,
            "actual_seconds": self.actual_seconds,
            "quality": self.quality,
            "provider_earned_sol": round(self.provider_earned_sol, 6),
            "created_at": self.created_at,
            "closed_at": self.closed_at,
        }


_jobs: dict[str, Job] = {}


class JobEngine:
    """Job lifecycle: quote → submit (route + occupy GPU) → complete/fail
    (settle SOL, pay provider with reputation bonus, free GPU, update reputation)."""

    def __init__(self, solana, catalog, pricing, providers, router, config=Config):
        self.solana = solana
        self.catalog = catalog
        self.pricing = pricing
        self.providers = providers
        self.router = router
        self.config = config

    def network_utilization(self) -> float:
        provs = self.providers.list_all()
        total = sum(p.gpus for p in provs)
        busy = sum(p.busy for p in provs)
        return safe_div(busy, total)

    def quote(self, task_key: str, units_multiple: float = 1.0):
        task = self.catalog.get(task_key)
        return self.pricing.quote(task, units_multiple, self.network_utilization(),
                                  self.solana.sol_price_usd())

    def submit(self, requester: str, task_key: str, units_multiple: float = 1.0) -> Job:
        task = self.catalog.get(task_key)
        q = self.quote(task_key, units_multiple)
        provider = self.router.pick()   # reputation-weighted
        provider.busy += 1              # occupy a GPU
        fee = bps(q.sol_cost, self.config.PROTOCOL_FEE_BPS)
        job = Job(
            id=new_id("job"),
            requester=requester,
            task_key=task_key,
            units_multiple=units_multiple,
            provider_id=provider.id,
            est_seconds=task.est_seconds * units_multiple,
            sol_cost=q.sol_cost,
            fee_sol=fee,
            status="running",
            created_at=utcnow_iso(),
        )
        _jobs[job.id] = job
        log.info("submitted %s: %s x%.1f → provider %s", job.id, task_key,
                 units_multiple, provider.id)
        return job

    def complete(self, job_id: str, actual_seconds: float = None,
                 quality: float = 0.9) -> Job:
        job = self._require(job_id)
        if job.status != "running":
            raise ValueError(f"job is not running (status={job.status})")
        provider = self.providers.get(job.provider_id)
        if actual_seconds is None:
            actual_seconds = job.est_seconds
        speed_ratio = safe_div(actual_seconds, job.est_seconds, default=1.0)

        # settle: provider earns cost minus fee, plus a reputation bonus
        net = job.sol_cost - job.fee_sol
        bonus = net * self.providers.earnings_bonus(provider.id)
        earned = net + bonus
        provider.earnings_sol += earned
        provider.busy = max(0, provider.busy - 1)

        job.status = "completed"
        job.actual_seconds = actual_seconds
        job.quality = quality
        job.provider_earned_sol = earned
        job.closed_at = utcnow_iso()
        self.providers.record_result(provider.id, success=True,
                                     speed_ratio=speed_ratio, quality=quality)
        log.info("completed %s: provider earned %.6f SOL (speed %.2f, quality %.2f)",
                 job_id, earned, speed_ratio, quality)
        return job

    def fail(self, job_id: str, reason: str = "execution error") -> Job:
        job = self._require(job_id)
        if job.status != "running":
            raise ValueError(f"job is not running (status={job.status})")
        provider = self.providers.get(job.provider_id)
        provider.busy = max(0, provider.busy - 1)
        job.status = "failed"
        job.closed_at = utcnow_iso()
        self.providers.record_result(provider.id, success=False)
        log.info("failed %s on provider %s: %s", job_id, provider.id, reason)
        return job

    def get(self, job_id: str) -> Job:
        return self._require(job_id)

    def list_jobs(self, requester: str = None) -> list[Job]:
        jobs = list(_jobs.values())
        if requester:
            jobs = [j for j in jobs if j.requester == requester]
        return jobs

    def _require(self, job_id: str) -> Job:
        job = _jobs.get(job_id)
        if not job:
            raise ValueError(f"job not found: {job_id}")
        return job
