from flask import Blueprint, jsonify, request
from ..services import registry as R

bp = Blueprint("bot", __name__)


@bp.post("/bot/quote")
def quote():
    d = request.get_json(force=True) or {}
    try:
        q = R.jobs.quote(d["task_key"], float(d.get("units_multiple", 1.0)))
        return jsonify(q.to_dict())
    except (KeyError, ValueError) as e:
        return jsonify({"error": str(e)}), 400


@bp.post("/bot/request")
def request_task():
    """Plain-language task request via the bot: NL → task spec → priced quote."""
    d = request.get_json(force=True) or {}
    try:
        return jsonify(R.planner.plan(d["message"]))
    except (KeyError, ValueError) as e:
        return jsonify({"error": str(e)}), 400
