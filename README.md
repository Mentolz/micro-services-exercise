To start the aplication run

```
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

To run test
```
poetry run pytest -vv
```

To consult the coverage report run
```
poetry run pytest --cov-report html --cov=app app/tests/; open htmlcov/index.html
```

To consult and play with the api you can go to
```
localhost:8000/docs#
```

## Instalation Steps

### Requirements
- [Poetry](https://python-poetry.org/docs/#installation)
- Python 3.9

```
$ poetry install
```