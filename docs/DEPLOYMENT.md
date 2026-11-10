# Deployment — Student Portfolio Showcase

## Host and why

**Render** (render.com), free tier. Chosen because it deploys straight from
a GitHub repo with no credit card, gives 750 free instance-hours/month, and
supports both a Python web service and a managed Postgres database on the
free tier.

### Deviation from the SAD: production database is Postgres, not SQLite

The SAD and the course decisions log specify SQLite. That's followed for
local development (see `app/__init__.py` — SQLite is still the default
when `DATABASE_URL` is unset). For the **public deployment specifically**,
this is a documented deviation (permitted under SAD §10.6):

Render's free web services have an **ephemeral filesystem** — anything
written to disk, including a local SQLite file, is wiped on every restart
or spin-down (free services sleep after 15 minutes idle and restart on the
next request). That directly breaks SRS requirement **SPS-FR-019**
("Persist user and portfolio records across application restarts") and
acceptance criterion **SPS-AT-004**. Using Render's free managed Postgres
database instead keeps data across restarts. The app already supports this
without any code changes beyond one normalisation line in `create_app()`
(Render hands out `postgres://` URLs; SQLAlchemy 1.4+ wants
`postgresql://`) — it reads the database location from the `DATABASE_URL`
environment variable and falls back to SQLite only when that variable is
unset.

## One-time setup

1. Create a free account at [render.com](https://render.com) (GitHub sign-in is fine).
2. From the Render dashboard: **New → Blueprint**, and point it at this
   GitHub repository (`nishithasathya/student-portfolio-showcase`), branch
   `main`. Render will read `render.yaml` at the repo root and provision:
   - a free **Web Service** (`student-portfolio-showcase`) that runs
     `pip install -r requirements.txt` then
     `gunicorn --bind 0.0.0.0:$PORT run:app`
   - a free **PostgreSQL** database (`student-portfolio-db`)
   - a generated `SECRET_KEY` and a `DATABASE_URL` wired automatically from
     the database to the web service — you do not type either of these in.
3. Click **Apply**. First deploy takes a few minutes.
4. Once live, open the assigned `https://<something>.onrender.com` URL and
   confirm `/health` returns `{"status": "healthy"}`.

The start command binds to `0.0.0.0:$PORT` because Render requires the
process to listen on the platform-assigned port. `run:app` loads the Flask
app object created in `run.py`.

If you'd rather configure it by hand instead of using the Blueprint:
New → Web Service → connect the repo → Build Command
`pip install -r requirements.txt` → Start Command
`gunicorn --bind 0.0.0.0:$PORT run:app` →
add environment variables `SECRET_KEY` (click "Generate") and `DATABASE_URL`
(copy the Internal Database URL from a separately-created Render Postgres
instance).

## Environment variables

| Variable | Required in production | Purpose |
|---|---|---|
| `SECRET_KEY` | Yes | Flask session signing. Must not be the `development-only-key` default. |
| `DATABASE_URL` | Yes | Postgres connection string. Unset = falls back to local SQLite (dev only). |
| `PYTHON_VERSION` | Set by Blueprint | Pins the Render runtime to Python 3.11.9, matching CI. |
| `PORT` | Set by Render | Port Gunicorn must bind. Do not hard-code it. |

Never commit real values for either secret — `.env.example` documents the names
only, and `.env` is already git-ignored.

## Verification checklist

Run through this after every deploy, not just the first one:

- [ ] `GET /health` → `200 {"status": "healthy"}`
- [ ] Register a throwaway test account, log in, log out
- [ ] Create a skill/project/achievement, confirm it's still there after
      reloading the page (proves the DB is the Postgres instance, not an
      ephemeral local file)
- [ ] Publish the test portfolio, open `/p/<slug>` in a private/incognito
      window (no session cookie) and confirm it's visible
- [ ] Unpublish it and confirm the same URL now returns 404
- [ ] Confirm the response headers / page source contain no stack traces
      or secret values
- [ ] Record the live URL in the project README once confirmed (SAD §10.3
      requires this)

## Known limitations

- Free web services spin down after 15 minutes of inactivity; the first
  request after that takes roughly a minute to wake back up. This is
  expected, not a bug — mention it during the demo if the first load is slow.
- Free Postgres databases expire 30 days after creation unless upgraded;
  for a one-off evaluation this is not a concern, but don't let the
  database go unused for a month before the demo.

## Recovery if deployment fails

1. Check the **Logs** tab on the Render service first — build failures and
   runtime crashes both show there.
2. If the build fails on a dependency, confirm `requirements.txt` installs
   cleanly locally with the exact same Python version (3.11) before
   re-deploying.
3. If the app boots but `/health` 500s, check that `DATABASE_URL` is set
   and reachable — a missing/incorrect connection string is the most common
   cause.
4. As a fallback for the demo, run the app locally (`python run.py`) and
   present from there while the hosted deployment is fixed — SAD §9 lists
   "retain local run as fallback" as the accepted mitigation for hosting
   unavailability.
