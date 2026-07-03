from flask import Blueprint, request, jsonify, g

from infra.db import get_db
from infra.repos.issue_repo import SQLiteIssueRepo
from infra.repos.project_repo import SQLiteProjectRepo
from services.issue_service import (
    IssueService,
    IssueNotFoundError,
    IssuePermissionError,
    InvalidStatusTransitionError,
    IssueServiceException,
)
from api.middlewares import jwt_required


issue_bp = Blueprint("issues", __name__, url_prefix="/projects/<int:project_id>/issues")


def get_issue_service() -> IssueService:
    db = get_db()
    return IssueService(SQLiteIssueRepo(db), SQLiteProjectRepo(db))


def _issue_to_dict(issue):
    return {
        "id": issue.id,
        "project_id": issue.project_id,
        "title": issue.title,
        "description": issue.description,
        "status": issue.status,
        "priority": issue.priority,
    }


@issue_bp.route("", methods=["POST"])
@jwt_required
def create_issue(project_id):
    data = request.get_json(silent=True) or {}
    title = data.get("title")
    description = data.get("description")
    priority = data.get("priority")

    if not title:
        return jsonify({"error": "title is required"}), 400

    service = get_issue_service()

    try:
        issue = service.create(g.user_id, project_id, title, description, priority)
    except IssueNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except IssuePermissionError as e:
        return jsonify({"error": str(e)}), 403
    except IssueServiceException as e:
        return jsonify({"error": str(e)}), 400

    return jsonify(_issue_to_dict(issue)), 201


@issue_bp.route("", methods=["GET"])
@jwt_required
def list_issues(project_id):
    status = request.args.get("status")
    priority = request.args.get("priority")

    service = get_issue_service()

    try:
        issues = service.list_for_project(g.user_id, project_id, status, priority)
    except IssueNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except IssuePermissionError as e:
        return jsonify({"error": str(e)}), 403

    return jsonify([_issue_to_dict(i) for i in issues]), 200


@issue_bp.route("/<int:issue_id>", methods=["GET"])
@jwt_required
def get_issue(project_id, issue_id):
    service = get_issue_service()

    try:
        issue = service.get_owned(g.user_id, project_id, issue_id)
    except IssueNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except IssuePermissionError as e:
        return jsonify({"error": str(e)}), 403

    return jsonify(_issue_to_dict(issue)), 200


@issue_bp.route("/<int:issue_id>", methods=["PUT"])
@jwt_required
def update_issue(project_id, issue_id):
    data = request.get_json(silent=True) or {}
    title = data.get("title")
    description = data.get("description")
    status = data.get("status")
    priority = data.get("priority")

    if not title:
        return jsonify({"error": "title is required"}), 400

    service = get_issue_service()

    try:
        issue = service.update(g.user_id, project_id, issue_id, title, description, status, priority)
    except IssueNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except IssuePermissionError as e:
        return jsonify({"error": str(e)}), 403
    except InvalidStatusTransitionError as e:
        return jsonify({"error": str(e)}), 409
    except IssueServiceException as e:
        return jsonify({"error": str(e)}), 400

    return jsonify(_issue_to_dict(issue)), 200


@issue_bp.route("/<int:issue_id>", methods=["DELETE"])
@jwt_required
def delete_issue(project_id, issue_id):
    service = get_issue_service()

    try:
        service.delete(g.user_id, project_id, issue_id)
    except IssueNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except IssuePermissionError as e:
        return jsonify({"error": str(e)}), 403

    return "", 204
