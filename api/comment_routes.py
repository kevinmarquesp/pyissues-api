from flask import Blueprint, request, jsonify, g

from infra.db import get_db
from infra.repos.comment_repo import SQLiteCommentRepo
from infra.repos.issue_repo import SQLiteIssueRepo
from infra.repos.project_repo import SQLiteProjectRepo
from services.comment_service import (
    CommentService,
    CommentNotFoundError,
    CommentPermissionError,
    CommentServiceException,
)
from api.middlewares import jwt_required


comment_bp = Blueprint(
    "comments", __name__,
    url_prefix="/projects/<int:project_id>/issues/<int:issue_id>/comments"
)


def get_comment_service() -> CommentService:
    db = get_db()
    return CommentService(SQLiteCommentRepo(db), SQLiteIssueRepo(db), SQLiteProjectRepo(db))


def _comment_to_dict(comment):
    return {
        "id": comment.id,
        "issue_id": comment.issue_id,
        "user_id": comment.user_id,
        "body": comment.body,
    }


@comment_bp.route("", methods=["POST"])
@jwt_required
def create_comment(project_id, issue_id):
    data = request.get_json(silent=True) or {}
    body = data.get("body")

    if not body:
        return jsonify({"error": "body is required"}), 400

    service = get_comment_service()

    try:
        comment = service.create(g.user_id, project_id, issue_id, body)
    except CommentNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except CommentPermissionError as e:
        return jsonify({"error": str(e)}), 403
    except CommentServiceException as e:
        return jsonify({"error": str(e)}), 400

    return jsonify(_comment_to_dict(comment)), 201


@comment_bp.route("", methods=["GET"])
@jwt_required
def list_comments(project_id, issue_id):
    service = get_comment_service()

    try:
        comments = service.list_for_issue(g.user_id, project_id, issue_id)
    except CommentNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except CommentPermissionError as e:
        return jsonify({"error": str(e)}), 403

    return jsonify([_comment_to_dict(c) for c in comments]), 200


@comment_bp.route("/<int:comment_id>", methods=["GET"])
@jwt_required
def get_comment(project_id, issue_id, comment_id):
    service = get_comment_service()

    try:
        comment = service.get_owned(g.user_id, project_id, issue_id, comment_id)
    except CommentNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except CommentPermissionError as e:
        return jsonify({"error": str(e)}), 403

    return jsonify(_comment_to_dict(comment)), 200


@comment_bp.route("/<int:comment_id>", methods=["PUT"])
@jwt_required
def update_comment(project_id, issue_id, comment_id):
    data = request.get_json(silent=True) or {}
    body = data.get("body")

    if not body:
        return jsonify({"error": "body is required"}), 400

    service = get_comment_service()

    try:
        comment = service.update(g.user_id, project_id, issue_id, comment_id, body)
    except CommentNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except CommentPermissionError as e:
        return jsonify({"error": str(e)}), 403

    return jsonify(_comment_to_dict(comment)), 200


@comment_bp.route("/<int:comment_id>", methods=["DELETE"])
@jwt_required
def delete_comment(project_id, issue_id, comment_id):
    service = get_comment_service()

    try:
        service.delete(g.user_id, project_id, issue_id, comment_id)
    except CommentNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except CommentPermissionError as e:
        return jsonify({"error": str(e)}), 403

    return "", 204
