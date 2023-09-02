set -xe
# Run tests
poetry run pytest --cov-report=term-missing --cov-report html:htmlcov --cov-config=pyproject.toml --cov=chemcloud --cov=tests .
