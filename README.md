# student-portfolio-showcase
Student Portfolio Showcase — SE Lab Jackfruit Problem

A web application for students to showcase projects, explore peer portfolios, and endorse other students’ work.

Technology Stack

* Python 3.11
* Flask, Flask-SQLAlchemy, Flask-Login
* SQLite locally, PostgreSQL on Render
* Gunicorn (production server)
* pytest
* Ruff
* GitHub Actions
* Render (deployment)

Current Features

* Registration, login and logout (hashed passwords, session auth)
* Owner-managed profile, skills, projects and achievements/certifications
* Portfolio publish/unpublish and a public read-only view at `/p/<slug>`
* Server-side ownership checks on every write (SPS-SEC-002)
* Application health-check endpoint
* Automated tests
* Automated code-quality checks
* Continuous integration using GitHub Actions

See [`docs/API_CONTRACT.md`](docs/API_CONTRACT.md) for the full endpoint
reference used by the frontend and test suite.

Project Structure

app/                     Flask application
tests/                   Automated tests
.github/workflows/       GitHub Actions workflows
run.py                   Application entry point
requirements.txt          Python dependencies
pyproject.toml            Tool configuration

Local Setup

Create a virtual environment:

python3 -m venv .venv

Activate it on macOS:

source .venv/bin/activate

Install dependencies:

python -m pip install -r requirements.txt

Run the application:

python run.py

Open http://127.0.0.1:5000/ in your browser.

The health-check endpoint is available at /health.

Run Automated Tests

python -m pytest -v

Run Code-Quality Checks

ruff check .

Continuous Integration

GitHub Actions runs code-quality checks and automated tests on pushes to main and pull requests targeting main. The workflow file is unchanged: `.github/workflows/ci.yml`.

See [`docs/CICD_EXPLANATION.md`](docs/CICD_EXPLANATION.md) for how CI relates to delivery, and how to demonstrate a passing and a failing run.

Deployment

Production is configured for Render in `render.yaml` and `Procfile`. The app is served with Gunicorn and uses PostgreSQL when `DATABASE_URL` is set. Local runs still use SQLite.

See [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) for the one-time Render setup, environment variables, and the post-deploy checklist. Record the live URL here after the first successful deploy.

Team Development

The team uses GitHub branches and pull requests to integrate changes. Features should include appropriate automated tests and pass the required CI checks before merging.