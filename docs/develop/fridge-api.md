# FRIDGE API

The FRIDGE API is a REST API used for interacting with services in the isolated cluster.

It was developed in Python with [FastAPI](https://fastapi.tiangolo.com/).

## Local Development

To run the `fridge-job-api` locally:

```bash
uv sync
uv run fastapi dev app/main.py
```

The API will be available at `http://localhost:8000`, with OpenAPI docs at `http://localhost:8000/docs`.

See [`fridge-job-api/README.md`](fridge-job-api/README.md) for configuration details, and the [developer documentation](https://alan-turing-institute.github.io/fridge/develop/target/) for broader contributor guidance.
