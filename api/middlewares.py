from functools import wraps
from flask import request, jsonify, g

from infra.db import get_db
from infra.repos.user_repo import SQLiteUserRepo
from services.auth_service import AuthService, AuthServiceException


def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "missing or invalid authorization header"}), 401

        token = auth_header.removeprefix("Bearer ").strip()

        repo = SQLiteUserRepo(get_db())
        auth_service = AuthService(repo)

        try:
            payload = auth_service.decode_token(token)
        except AuthServiceException as e:
            return jsonify({"error": str(e)}), 401

        g.user_id = int(payload["sub"])
        g.username = payload["username"]

        return f(*args, **kwargs)

    return decorated
