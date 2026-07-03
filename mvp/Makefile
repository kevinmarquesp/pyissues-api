PYTHON = .venv/bin/python
PYTEST = .venv/bin/pytest
SQLITE3 = /usr/bin/sqlite3

RUN_SCRIPT_FILE = app.py
SCHEMA_SQL_FILE = infra/sql/schema.sql
DATABASE_FILE = db.sqlite3


.PHONY: install
install:
	$(PYTHON) -m pip install -r 'requirements.txt'

.PHONY: run
run:
	$(PYTHON) '$(RUN_SCRIPT_FILE)'

.PHONY: test
test:
	$(PYTEST) -v

.PHONY: db/init
db/init:
	$(SQLITE3) $(DATABASE_FILE) < $(SCHEMA_SQL_FILE)

.PHONY: clean
clean:
	rm -vrf __pycache__ **/__pycache__ .pytest_cache $(DATABASE_FILE)
