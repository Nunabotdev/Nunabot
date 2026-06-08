import sys, os
from unittest.mock import MagicMock
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.services.solana_client import SolanaClient
from app.services.catalog import TaskCatalog
from app.services.pricing import PricingEngine
from app.services.providers import ProviderRegistry, _providers
from app.services.router import JobRouter
from app.services.jobs import JobEngine, _jobs
from app.services.agents import AgentLayer, _sessions
from app.config import Config


def setup_function():
    _providers.clear()
    _jobs.clear()
    _sessions.clear()


def make():
    sol = MagicMock(spec=SolanaClient)
    sol.sol_price_usd.return_value = 150.0
    reg = ProviderRegistry(Config)
    router = JobRouter(reg, Config)
    eng = JobEngine(sol, TaskCatalog(), PricingEngine(Config), reg, router, Config)
    reg.register("op", 8)
    return eng, reg, AgentLayer(eng, Config)


# --- pricing / catalog ---
def test_catalog_supported():
    cat = TaskCatalog()
    assert cat.is_supported("inference")
    assert not cat.is_supported("mining")


def test_heavier_task_costs_more():
    sol = 150.0
    p = PricingEngine(Config)
    cat = TaskCatalog()
    cheap = p.quote(cat.get("inference"), 1.0, 0.0, sol)
    pricey = p.quote(cat.get("generation"), 1.0, 0.0, sol)
    assert pricey.sol_cost > cheap.sol_cost


def test_units_multiple_scales_cost():
    p = PricingEngine(Config)
    cat = TaskCatalog()
    one = p.quote(cat.get("inference"), 1.0, 0.0, 150.0)
    three = p.quote(cat.get("inference"), 3.0, 0.0, 150.0)
    assert three.sol_cost > one.sol_cost


def test_demand_multiplier_rises():
    p = PricingEngine(Config)
    assert p.demand_multiplier(0.0) == 1.0
    assert p.demand_multiplier(1.0) > p.demand_multiplier(0.0)


# --- agents ---
def test_open_session():
    eng, reg, agents = make()
    s = agents.open_session("agent.a", 1.0)
    assert s.remaining_sol == 1.0
    assert s.status == "open"


def test_session_rejects_zero_budget():
    eng, reg, agents = make()
    try:
        agents.open_session("agent.a", 0)
        assert False
    except ValueError:
        pass


def test_agent_runs_and_debits_budget():
    eng, reg, agents = make()
    s = agents.open_session("agent.a", 1.0)
    before = s.remaining_sol
    res = agents.run(s.id, "inference")
    assert res["job"]["status"] == "completed"
    assert agents.get_session(s.id).remaining_sol < before
    assert len(agents.get_session(s.id).job_ids) == 1


def test_agent_chains_until_budget_exhausted():
    eng, reg, agents = make()
    # tiny budget: enough for a couple of cheap jobs, not many
    q = eng.quote("inference")
    s = agents.open_session("agent.a", q.sol_cost * 2.5)
    ran = 0
    for _ in range(10):
        try:
            agents.run(s.id, "inference")
            ran += 1
        except ValueError:
            break
    assert ran == 2  # only 2 fit in the budget
    assert agents.get_session(s.id).remaining_sol < q.sol_cost


def test_run_on_closed_session_fails():
    eng, reg, agents = make()
    s = agents.open_session("agent.a", 1.0)
    agents.close_session(s.id)
    try:
        agents.run(s.id, "inference")
        assert False
    except ValueError:
        pass
