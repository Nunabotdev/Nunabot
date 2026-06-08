from flask import Blueprint, jsonify, request
from ..services import registry as R

bp = Blueprint("provider", __name__)


@bp.post("/provider/register")
def register():
    d = request.get_json(force=True) or {}
    try:
        p = R.providers.register(d["operator"], int(d["gpus"]))
        return jsonify(R.providers.reputation_view(p.id)), 201
    except (KeyError, ValueError) as e:
        return jsonify({"error": str(e)}), 400


@bp.get("/providers")
def list_providers():
    ranked = R.router.ranked() if request.args.get("ranked") else R.providers.list_all()
    return jsonify([R.providers.reputation_view(p.id) for p in ranked])


@bp.get("/provider/<provider_id>")
def get_provider(provider_id):
    try:
        return jsonify(R.providers.reputation_view(provider_id))
    except ValueError as e:
        return jsonify({"error": str(e)}), 404


@bp.post("/provider/<provider_id>/heartbeat")
def heartbeat(provider_id):
    d = request.get_json(silent=True) or {}
    try:
        R.providers.heartbeat(provider_id, online=bool(d.get("online", True)))
        return jsonify(R.providers.reputation_view(provider_id))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
