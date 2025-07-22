# jira-mcp-server

A Python backend server for the MCP (Multi-Channel Platform) project, designed to integrate with Jira and provide an API for various operations. The server uses FastAPI/Uvicorn and can be easily set up with `pyenv` and `venv` for isolated development environments.

## Features
- SSE (Server-Sent Events) support
- Integration with Jira APIs
- RESTful endpoints
- Environment variable management with `.env`
- Easy setup and dependency management

## Requirements
- Python 3.10.14 (recommended, managed with [pyenv](https://github.com/pyenv/pyenv))
- [pip](https://pip.pypa.io/en/stable/)
- [venv](https://docs.python.org/3/library/venv.html)

## Setup Instructions

### 1. Install Python Version (if needed)
```sh
pyenv install 3.10.14
pyenv local 3.10.14
```

### 2. Create Virtual Environment
```sh
make env
```

### 3. Activate Virtual Environment
```sh
source .venv/bin/activate
```

### 4. Install Dependencies
```sh
make install
```

### 5. Run the Server
```sh
make start
```
The server will start at [http://localhost:9999](http://localhost:9999)

npx @modelcontextprotocol/inspector uv \
  --directory /Users/yinseng/Documents/Projects/slash/mcp-server/jira-mcp-server run src/main.py

## Makefile Commands
| Command        | Description                                  |
| -------------- | -------------------------------------------- |
| make env       | Create a virtual environment in `.venv`      |
| make install   | Install dependencies from `requirements.txt` |
| make install-dev | Install dev dependencies                   |
| make start     | Run the server (`src/main.py`)               |
| make activate  | Show how to activate the virtualenv          |
| make deactivate| Show how to deactivate the virtualenv        |

## Environment Variables
Create a `.env` file in the project root for environment-specific settings (see `.env.example` if available).

## Notes
- Ensure your shell is configured to use `pyenv` shims (see [pyenv docs](https://github.com/pyenv/pyenv#installation)).
- If you encounter issues with Python versions, check your `PATH` and shell initialization files.

## License
MIT
