"""End-to-end Nunabot walkthrough with a mocked SOL price (no network/keys).

Shows: providers register, a reliable fast provider builds reputation and starts
winning the router, the bot prices and runs jobs, and an AI agent opens a budget
session and autonomously chains jobs until the budget runs low.
"""
import sys, os
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.config import Config
from app.services.solana_client import SolanaClient
from app.services.catalog import TaskCatalog
from app.services.pricing import PricingEngine
from app.services.providers import ProviderRegistry, _providers
from app.services.router import JobRouter
from app.services.jobs import JobEngine, _jobs
from app.services.agents import AgentLayer, _sessions


def build():
    sol = MagicMock(spec=SolanaClient)
    sol.sol_price_usd.return_value = 150.0
    providers = ProviderRegistry(Config)
    router = JobRouter(providers, Config)
    jobs = JobEngine(sol, TaskCatalog(), PricingEngine(Config), providers, router, Config)
    agents = AgentLayer(jobs, Config)
    return jobs, providers, router, agents


def reset():
    _providers.clear(); _jobs.clear(); _sessions.clear()


def main():
    reset()
    jobs, providers, router, agents = build()
    print("Nunabot Simulation")
    print("=" * 58)

    fast = providers.register("fastOps", 4)
    slow = providers.register("slowOps", 4)
    print(f"\nProviders: {fast.operator} (rep {providers.reputation(fast.id)}), "
          f"{slow.operator} (rep {providers.reputation(slow.id)})")

    # fast provider builds a strong record; slow one is flaky
    for _ in range(30):
        providers.heartbeat(fast.id, online=True)
        providers.record_result(fast.id, success=True, speed_ratio=0.7, quality=0.95)
    for _ in range(30):
        providers.heartbeat(slow.id, online=(_ % 3 != 0))   # misses heartbeats
        if _ % 4 == 0:
            providers.record_result(slow.id, success=False)
        else:
            providers.record_result(slow.id, success=True, speed_ratio=1.6, quality=0.7)

    print(f"\nAfter activity:")
    print(f"  {fast.operator}: rep {providers.reputation(fast.id)} "
          f"({providers.tier(fast.id)}) — {providers.components(fast.id)}")
    print(f"  {slow.operator}: rep {providers.reputation(slow.id)} "
          f"({providers.tier(slow.id)}) — {providers.components(slow.id)}")
    print(f"  router picks: {providers.get(router.pick().id).operator} (reputation wins)")

    print(f"\nBot jobs:")
    for task in ["inference", "generation", "market"]:
        q = jobs.quote(task)
        job = jobs.submit("user.alice", task)
        jobs.complete(job.id, quality=0.92)
        p = providers.get(job.provider_id)
        print(f"  {task:11s} {q.sol_cost:.6f} SOL → {p.operator} "
              f"earned {job.provider_earned_sol:.6f} SOL")

    print(f"\nAgent session (autonomous chaining):")
    s = agents.open_session("agent.zeta", budget_sol=0.05)
    print(f"  opened with {s.budget_sol:.4f} SOL budget")
    ran = 0
    for task in ["inference", "analysis", "inference", "generation", "inference"]:
        try:
            res = agents.run(s.id, task)
            ran += 1
        except ValueError as e:
            print(f"  stopped: {e}")
            break
    s = agents.get_session(s.id)
    print(f"  agent ran {ran} jobs, spent {s.spent_sol:.6f} SOL, "
          f"{s.remaining_sol:.6f} SOL left")

    print("\n" + "=" * 58)
    print("Reputation routes the work, the bot prices it, and agents pay from a "
          "budget. That's Nunabot.")


if __name__ == "__main__":
    main()
