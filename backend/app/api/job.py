from flask import Blueprint, jsonify, request
from ..services import registry as R

bp = Blueprint("job", __name__)


@bp.post("/job/submit")
def submit():
    d = request.get_json(force=True) or {}
    try:
        job = R.jobs.submit(d["requester"], d["task_key"], float(d.get("units_multiple", 1.0)))
        return jsonify(job.to_dict()), 201
    except (KeyError, ValueError) as e:
        return jsonify({"error": str(e)}), 400


@bp.post("/job/<job_id>/complete")
def complete(job_id):
    d = request.get_json(silent=True) or {}
    try:
        job = R.jobs.complete(job_id, actual_seconds=d.get("actual_seconds"),
                              quality=float(d.get("quality", 0.9)))
        return jsonify(job.to_dict())
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@bp.post("/job/<job_id>/fail")
def fail(job_id):
    d = request.get_json(silent=True) or {}
    try:
        return jsonify(R.jobs.fail(job_id, reason=d.get("reason", "execution error")).to_dict())
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@bp.get("/job/<job_id>")
def get_job(job_id):
    try:
        return jsonify(R.jobs.get(job_id).to_dict())
    except ValueError as e:
        return jsonify({"error": str(e)}), 404


@bp.get("/job/list")
def list_jobs():
    requester = request.args.get("requester")
    return jsonify([j.to_dict() for j in R.jobs.list_jobs(requester)])
