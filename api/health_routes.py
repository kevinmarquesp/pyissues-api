from flask import Blueprint, jsonify
from infra.db import get_db
from sqlite3 import Error as sqlite3_Error

health_bp = Blueprint('health', __name__)

@health_bp.get('/health')
def health():
  db = get_db()

  try:
    db.execute('INSERT INTO health DEFAULT VALUES')
    db.commit()

    row = db.execute(
      'SELECT id, checked_at FROM health ORDER BY id DESC LIMIT 1').fetchone()

    return jsonify({
      'status': 'ok',
      'database': 'connected',
      'details': dict(row)}), 200

  except sqlite3_Error as e:
    return jsonify({
      'status': 'error',
      'database': 'unreachable',
      'error': str(e)}), 503
