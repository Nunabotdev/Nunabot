from dataclasses import dataclass
from ..config import Config
from ..utils import clamp, safe_div


@dataclass
class PriceQuote:
    task_key: str
    compute_units: float
    demand_multiplier: float
    usd_cost: float
    sol_cost: float
    sol_price_usd: float

    def to_dict(self) -> dict:
        return {
            "task_key": self.task_key,
            "compute_units": round(self.compute_units, 3),
            "demand_multiplier": round(self.demand_multiplier, 4),
            "usd_cost": round(self.usd_cost, 4),
            "sol_cost": round(self.sol_cost, 6),
            "sol_price_usd": round(self.sol_price_usd, 2),
        }


class PricingEngine:
    """Job price = compute_units × per-unit baseline × demand multiplier,
    converted to SOL at the live price. Demand rises with network utilization."""

    def __init__(self, config=Config):
        self.config = config

    def demand_multiplier(self, utilization: float) -> float:
        return 1.0 + self.config.DEMAND_PRICE_SLOPE * clamp(utilization, 0.0, 1.0)

    def quote(self, task: "TaskType", units_multiple: float, utilization: float,
              sol_price_usd: float) -> PriceQuote:
        if units_multiple <= 0:
            raise ValueError("units_multiple must be positive")
        cu = task.compute_units * units_multiple
        dm = self.demand_multiplier(utilization)
        usd = cu * self.config.COMPUTE_UNIT_USD * dm
        sol = safe_div(usd, sol_price_usd)
        return PriceQuote(task.key, cu, dm, usd, sol, sol_price_usd)
