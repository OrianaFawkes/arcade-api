# Arcade API

Backend API for **Arcade**.

## Getting started

### Option A: GitHub Codespaces

1. Open the repository on GitHub.

2. Select **Code → Codespaces** and create or open a Codespace.

3. Open a terminal in VS Code.

4. Verify the Python version:

   ```bash
   python --version
   ```

   The development environment should use Python 3.12.

5. Install dependencies if needed:

   ```bash
   python -m pip install -r requirements.txt -r requirements-dev.txt
   ```

6. Run the tests:

   ```bash
   python -m pytest
   ```

### Option B: Local development

Prerequisites: Git and Python 3.12.

Clone the repository and enter the project directory:

```bash
git clone https://github.com/OrianaFawkes/arcade-api
cd arcade-api
```

Create and activate a virtual environment.

**macOS / Linux:**

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

**Windows PowerShell:**

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies and run the tests:

```bash
python -m pip install -r requirements.txt -r requirements-dev.txt
python -m pytest
```

The virtual environment is local to your machine and should not be committed to Git.

## Running the API

Start the development server:

```bash
python -m uvicorn main:app --reload
```

Open these URLs in your browser:

* `/health` — basic application health check
* `/docs` — interactive Swagger API documentation
* `/openapi.json` — generated OpenAPI specification

In Codespaces, use the forwarded port URL shown in the **Ports** panel. Locally, the default address is `http://127.0.0.1:8000`.

Stop the server with `Ctrl+C`.

## Testing

Run the complete test suite:

```bash
python -m pytest
```

Run a particular test file:

```bash
python -m pytest tests/test_health.py
```

Tests are also run automatically by GitHub Actions when code is pushed or a pull request is opened.

## Git workflow

Keep `main` as the stable branch. Create a feature branch for new work:

```bash
git switch main
git pull
git switch -c feat/short-description
```

After implementing and testing the change:

```bash
python -m pytest
git add .
git commit -m "feat: describe the change"
git push -u origin feat/short-description
```

Open a pull request on GitHub, verify that CI passes, and merge the branch into `main` when ready.

Use descriptive branch names such as `feat/scores`, `fix/validation`, or `docs/readme`.

## Project structure

```text
arcade-api/
├── .devcontainer/       # Codespaces development environment
├── .github/workflows/   # CI workflows
├── tests/               # Automated tests
├── .gitignore
├── LICENSE
├── README.md
├── main.py              # FastAPI application
├── requirements.txt     # Application dependencies
└── requirements-dev.txt # Development and test dependencies
```
