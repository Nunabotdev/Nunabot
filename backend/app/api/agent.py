from flask import Blueprint, jsonify, request
from ..services import registry as R

bp = Blueprint("agent", __name__)


@bp.post("/agent/session")
def open_session():
    d = request.get_json(force=True) or {}
    try:
        s = R.agents.open_session(d["agent"], float(d["budget_sol"]))
        return jsonify(s.to_dict()), 201
    except (KeyError, ValueError) as e:
        return jsonify({"error": str(e)}), 400


@bp.post("/agent/<session_id>/run")
def run(session_id):
    d = request.get_json(force=True) or {}
    try:
        return jsonify(R.agents.run(session_id, d["task_key"],
                                    float(d.get("units_multiple", 1.0)),
                                    float(d.get("quality", 0.9))))
    except (KeyError, ValueError) as e:
        return jsonify({"error": str(e)}), 400


@bp.get("/agent/<session_id>")
def get_session(session_id):
    try:
        return jsonify(R.agents.get_session(session_id).to_dict())
    except ValueError as e:
        return jsonify({"error": str(e)}), 404


@bp.post("/agent/<session_id>/close")
def close_session(session_id):
    try:
        return jsonify(R.agents.close_session(session_id).to_dict())
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
