"""Shared service singletons wired together once and reused across requests."""
from ..config import Config
from .solana_client import SolanaClient
from .catalog import TaskCatalog
from .pricing import PricingEngine
from .providers import ProviderRegistry
from .router import JobRouter
from .jobs import JobEngine
from .agents import AgentLayer
from .planner import TaskPlanner

solana = SolanaClient(Config)
catalog = TaskCatalog()
pricing = PricingEngine(Config)
providers = ProviderRegistry(Config)
router = JobRouter(providers, Config)
jobs = JobEngine(solana, catalog, pricing, providers, router, Config)
agents = AgentLayer(jobs, Config)
planner = TaskPlanner(jobs, Config)
