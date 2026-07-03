from flask import Blueprint, request, jsonify

from infra.db import get_db
from infra.repos.user_repo import SQLiteUserRepo
from services.auth_service import AuthService, AuthServiceException


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


# constructs the auth service with the necessary dependencies
def get_auth_service() -> AuthService:
    repo = SQLiteUserRepo(get_db())
    return AuthService(repo)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "username, email and password are required"}), 400

    auth_service = get_auth_service()

    try:
        user = auth_service.register(username, email, password)
    except AuthServiceException as e:
        return jsonify({"error": str(e)}), 409  # conflict (duplicate user)

    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "username and password are required"}), 400

    auth_service = get_auth_service()

    try:
        token = auth_service.login(username, password)
    except AuthServiceException as e:
        return jsonify({"error": str(e)}), 401

    return jsonify({"token": token}), 200
