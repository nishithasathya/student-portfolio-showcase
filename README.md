# student-portfolio-showcase
Student Portfolio Showcase — SE Lab Jackfruit Problem

A web application for students to showcase projects, explore peer portfolios, and endorse other students’ work.

Technology Stack

* Python 3.11
* Flask
* SQLite (planned)
* pytest
* Ruff
* GitHub Actions

Current Features

* Basic Flask application
* Application health-check endpoint
* Automated tests
* Automated code-quality checks
* Continuous integration using GitHub Actions

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