from sqlite3 import connect, PARSE_DECLTYPES, Row
from flask import g, current_app
from pathlib import Path


def get_db():
  if 'db' in g:
    return g.db

  g.db = connect(
    current_app.config['SQLITE3_FILE'],
    detect_types=PARSE_DECLTYPES)
  g.db.row_factory = Row
  g.db.execute('PRAGMA foreign_keys = ON')  # fix foreign keys in SQLite3

  return g.db

def init_db():
  db = get_db()

  with open('infra/sql/schema.sql') as f:  # improve that later
    db.executescript(f.read())

  db.commit()
  db.close()


def close_db(e=None):
  db = g.pop('db', None) 

  if db is not None:
    db.close()
