mypy:
	poetry run mypy .

test:
	poetry run pytest -x --cov=core --cov=sqlalchemy-to-json-schema --cov-fail-under=90

install:
	poetry install --sync
