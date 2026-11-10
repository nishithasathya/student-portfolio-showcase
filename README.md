# student-portfolio-showcase
Student Portfolio Showcase — SE Lab Jackfruit Problem

A web application for students to showcase projects, explore peer portfolios, and endorse other students’ work.

Technology Stack

* Python 3.11
* Flask, Flask-SQLAlchemy, Flask-Login
* SQLite
* pytest
* Ruff
* GitHub Actions

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

GitHub Actions runs code-quality checks and automated tests on pushes to main and pull requests targeting main.

Team Development

The team uses GitHub branches and pull requests to integrate changes. Features should include appropriate automated tests and pass the required CI checks before merging.