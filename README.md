# second-brain

## Installation

Clone the repository and install dependencies:

```bash
git clone <repo-url>
cd second-brain
uv sync
```

## Usage

Via the CLI entrypoint:

```bash
uv run second_brain
```

With dev environment variables loaded:

```bash
uv run --env-file .env second_brain
```

Via Python module:

```bash
uv run python -m second_brain
```

## Environment Variables

Copy `.env.example` to `.env` for development defaults:

```bash
cp .env.example .env
```

Note: `uv run --env-file .env` loads the dev environment explicitly — there is no auto-loading.

| Variable    | Default    | Description                                          |
|-------------|------------|------------------------------------------------------|
| `LOG_LEVEL` | `INFO`     | Console log level. Set to `DEBUG` in `.env` for verbose output. |
| `LOG_FILE`  | `app.log`  | Path to the log file.                                |

## Testing

Run tests:

```bash
uv run pytest
```

Run tests with coverage:

```bash
uv run pytest --cov
```

## Documentation

Preview docs locally:

```bash
uv run python scripts/serve_docs.py
```

Build static docs:

```bash
uv run mkdocs build
```
