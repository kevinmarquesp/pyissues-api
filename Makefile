PYTHON = .venv/bin/python
PYTEST = .venv/bin/pytest

RUN_SCRIPT = run.py


.PHONY: install
install:
	$(PYTHON) -m pip install -r 'requirements.txt'

.PHONY: run
run:
	$(PYTHON) '$(RUN_SCRIPT)'

.PHONY: test
test:
	$(PYTEST) -v
