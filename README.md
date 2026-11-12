# student-portfolio-showcase
Student Portfolio Showcase — SE Lab Jackfruit Problem

A full-stack web application where a student registers, builds a portfolio
(profile, skills, projects, achievements/certifications), and publishes it
at a public, shareable URL. Visitors can view a published portfolio;
editing is restricted to its owner.

Technology Stack

* Python 3.11
* Flask, Flask-SQLAlchemy, Flask-Login
* SQLite locally, PostgreSQL on Render
* Gunicorn (production server)
* HTML / CSS / JavaScript (Jinja2 templates, no frontend framework)
* pytest, Ruff
* GitHub Actions
* Render (deployment)

Current Features

* Registration, login and logout (hashed passwords, session auth)
* Registration/login pages, a dashboard, and a portfolio editor (profile,
  skills, projects, achievements/certifications)
* Portfolio publish/unpublish and a public read-only page at `/u/<slug>`
  (backed by the JSON API at `/p/<slug>`)
* Server-side ownership checks on every write (SPS-SEC-002)
* Application health-check endpoint
* 58 automated tests covering auth, CRUD, access control, security
  hygiene and persistence (see [`docs/API_CONTRACT.md`](docs/API_CONTRACT.md)
  for the endpoint reference, and "Known limitations" below for test
  coverage that is *not* included)
* Automated code-quality checks (Ruff)
* Continuous integration using GitHub Actions, with branch protection on
  `main` requiring a passing check and 1 approving review
* Live deployment on Render with a PostgreSQL database

Project Structure

app/
  models/                SQLAlchemy models (User, Portfolio, Skill, Project, Achievement)
  auth/                  Register / login / logout routes
  portfolio/             Profile, skills, projects, achievements, publish — owner-only CRUD
  public/                Public JSON view of a published portfolio (/p/<slug>)
  views/                 Page routes that render the templates below
  templates/             Jinja2 page shells (register, login, dashboard, editor, public page)
  static/css, static/js  Styling and the frontend's API client + page logic
  validators.py, errors.py, extensions.py, __init__.py (app factory)
tests/                   58 automated tests (pytest)
docs/                    SRS, SAD, STP, API contract, CI/CD and deployment docs
.github/workflows/       GitHub Actions CI workflow
instance/                Local SQLite database (git-ignored)
run.py                   Local development entry point
Procfile, render.yaml    Production deployment config (Render)
.env.example             Documents SECRET_KEY / DATABASE_URL (never commit real values)
requirements.txt         Python dependencies
pyproject.toml           pytest / Ruff configuration

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

Live URL: https://student-portfolio-showcase.onrender.com

See [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) for the one-time Render setup, environment variables, and the post-deploy checklist.

Known Limitations

See [`docs/FINAL_EVALUATION.md`](docs/FINAL_EVALUATION.md) for the full
test summary, requirement traceability and honestly-documented gaps
(frontend has no automated tests of its own, no rate limiting on login,
performance/accessibility/compatibility were reviewed manually rather
than automated, and the TC-CI-02 intentional-failure demo has not been
run).

Team Development

The team uses GitHub branches and pull requests to integrate changes. Features should include appropriate automated tests and pass the required CI checks before merging.