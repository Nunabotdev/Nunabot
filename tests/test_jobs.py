import sys, os
from unittest.mock import MagicMock
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.services.solana_client import SolanaClient
from app.services.catalog import TaskCatalog
from app.services.pricing import PricingEngine
from app.services.providers import ProviderRegistry, _providers
from app.services.router import JobRouter
from app.services.jobs import JobEngine, _jobs
from app.config import Config


def setup_function():
    _providers.clear()
    _jobs.clear()


def make():
    sol = MagicMock(spec=SolanaClient)
    sol.sol_price_usd.return_value = 150.0
    reg = ProviderRegistry(Config)
    router = JobRouter(reg, Config)
    eng = JobEngine(sol, TaskCatalog(), PricingEngine(Config), reg, router, Config)
    return eng, reg


def test_quote_positive():
    eng, _ = make()
    q = eng.quote("generation")
    assert q.sol_cost > 0
    assert q.usd_cost > 0


def test_quote_unknown_task():
    eng, _ = make()
    try:
        eng.quote("mining")
        assert False
    except ValueError:
        pass


def test_submit_needs_provider():
    eng, _ = make()
    try:
        eng.submit("u", "inference")  # no providers registered
        assert False
    except ValueError:
        pass


def test_submit_occupies_gpu():
    eng, reg = make()
    p = reg.register("op", 2)
    job = eng.submit("u", "inference")
    assert job.status == "running"
    assert reg.get(p.id).busy == 1


def test_complete_settles_and_pays_provider():
    eng, reg = make()
    p = reg.register("op", 2)
    job = eng.submit("u", "generation")
    done = eng.complete(job.id, quality=0.95)
    assert done.status == "completed"
    assert done.provider_earned_sol > 0
    assert reg.get(p.id).busy == 0
    assert reg.get(p.id).completed_jobs == 1


def test_complete_updates_reputation_speed_quality():
    eng, reg = make()
    p = reg.register("op", 2)
    job = eng.submit("u", "inference")
    eng.complete(job.id, actual_seconds=job.est_seconds * 0.5, quality=0.99)
    prov = reg.get(p.id)
    assert prov.quality_samples == 1
    assert prov.speed_samples == 1
    assert prov.avg_speed_ratio < 1.0


def test_fail_frees_gpu_and_hits_reliability():
    eng, reg = make()
    p = reg.register("op", 2)
    job = eng.submit("u", "inference")
    eng.fail(job.id)
    prov = reg.get(p.id)
    assert prov.busy == 0
    assert prov.failed_jobs == 1
    assert eng.get(job.id).status == "failed"


def test_high_rep_provider_earns_bonus():
    eng, reg = make()
    p = reg.register("op", 2)
    # build reputation first
    for _ in range(40):
        reg.heartbeat(p.id, online=True)
        reg.record_result(p.id, success=True, speed_ratio=0.7, quality=0.97)
    job = eng.submit("u", "generation")
    done = eng.complete(job.id, quality=0.95)
    net = job.sol_cost - job.fee_sol
    assert done.provider_earned_sol > net  # bonus applied


def test_demand_rises_with_utilization():
    eng, reg = make()
    reg.register("op", 10)
    base = eng.quote("inference").demand_multiplier
    # occupy half the GPUs via jobs
    for _ in range(5):
        eng.submit("u", "inference")
    busy = eng.quote("inference").demand_multiplier
    assert busy > base


def test_fee_charged():
    eng, reg = make()
    reg.register("op", 2)
    job = eng.submit("u", "market")
    assert job.fee_sol > 0
