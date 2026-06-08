from flask import Blueprint, jsonify
from ..services import registry as R
from ..config import Config

bp = Blueprint("market", __name__)


@bp.get("/market")
def market():
    provs = R.providers.list_all()
    return jsonify({
        "protocol_fee_bps": Config.PROTOCOL_FEE_BPS,
        "providers": len(provs),
        "total_gpus": sum(p.gpus for p in provs),
        "busy_gpus": sum(p.busy for p in provs),
        "utilization": round(R.jobs.network_utilization(), 4),
        "sol_price_usd": round(R.solana.sol_price_usd(), 2),
    })


@bp.get("/catalog")
def catalog():
    util = R.jobs.network_utilization()
    sol = R.solana.sol_price_usd()
    out = []
    for t in R.catalog.list_all():
        q = R.pricing.quote(t, 1.0, util, sol)
        d = t.to_dict()
        d["sol_cost"] = q.to_dict()["sol_cost"]
        out.append(d)
    return jsonify(out)
