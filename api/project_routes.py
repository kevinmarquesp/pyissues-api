from flask import Blueprint, request, jsonify, g

from infra.db import get_db
from infra.repos.project_repo import SQLiteProjectRepo
from services.project_service import (
    ProjectService,
    ProjectNotFoundError,
    ProjectPermissionError,
)
from api.middlewares import jwt_required


project_bp = Blueprint("projects", __name__, url_prefix="/projects")


def get_project_service() -> ProjectService:
    repo = SQLiteProjectRepo(get_db())
    return ProjectService(repo)


def _project_to_dict(project):
    return {
        "id": project.id,
        "user_id": project.user_id,
        "name": project.name,
        "description": project.description,
    }


@project_bp.route("", methods=["POST"])
@jwt_required
def create_project():
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    description = data.get("description")

    if not name:
        return jsonify({"error": "name is required"}), 400

    service = get_project_service()
    project = service.create(g.user_id, name, description)

    return jsonify(_project_to_dict(project)), 201


@project_bp.route("", methods=["GET"])
@jwt_required
def list_projects():
    service = get_project_service()
    projects = service.list_for_user(g.user_id)

    return jsonify([_project_to_dict(p) for p in projects]), 200


@project_bp.route("/<int:project_id>", methods=["GET"])  # TODO: use str
@jwt_required
def get_project(project_id):
    service = get_project_service()

    try:
        project = service.get_owned(g.user_id, project_id)
    except ProjectNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except ProjectPermissionError as e:
        return jsonify({"error": str(e)}), 403

    return jsonify(_project_to_dict(project)), 200


@project_bp.route("/<int:project_id>", methods=["PUT"])
@jwt_required
def update_project(project_id):
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    description = data.get("description")

    if not name:
        return jsonify({"error": "name is required"}), 400

    service = get_project_service()

    try:
        project = service.update(g.user_id, project_id, name, description)
    except ProjectNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except ProjectPermissionError as e:
        return jsonify({"error": str(e)}), 403

    return jsonify(_project_to_dict(project)), 200


@project_bp.route("/<int:project_id>", methods=["DELETE"])
@jwt_required
def delete_project(project_id):
    service = get_project_service()

    try:
        service.delete(g.user_id, project_id)
    except ProjectNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except ProjectPermissionError as e:
        return jsonify({"error": str(e)}), 403

    return "", 204
