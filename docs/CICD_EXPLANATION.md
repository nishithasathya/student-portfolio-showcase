# CI/CD — Student Portfolio Showcase

## Definitions (for the evaluation)

- **Continuous Integration (CI)** — every push and pull request automatically
  triggers linting and the test suite, so integration problems are caught
  within minutes of being introduced rather than at the end of the project.
  This repo's CI is `.github/workflows/ci.yml`.
- **Continuous Delivery (CD)** — every change that passes CI is
  automatically built into a deployable artifact and is *one click away*
  from being released, but a human still decides when to actually release it.
- **Continuous Deployment** — the stricter version of CD: every change that
  passes CI is released automatically, with no human approval step.

**This project implements CI, and Continuous Delivery via Render's
GitHub-connected auto-deploy on merges to `main`** (Render redeploys
automatically whenever `main` updates — that's delivery). It is **not**
full Continuous Deployment, because merging a PR into `main` is still a
human decision (your own branch-protection workflow in section 7 of the
project brief), and the person merging is the one "deciding to release."

## Pipeline architecture

```
push / PR  →  GitHub Actions (ubuntu-latest)
                 ├─ checkout
                 ├─ setup Python 3.11
                 ├─ pip install -r requirements.txt
                 ├─ ruff check .          (fails the job on any lint error)
                 └─ pytest -v             (fails the job on any test failure)
                        │
              merge to main (manual, after review + green checks)
                        │
              Render auto-deploy (build: pip install -r requirements.txt
                                   start: gunicorn --bind 0.0.0.0:$PORT run:app)
```

The existing `Lint and Test` workflow is unchanged. Production dependencies
(`gunicorn`, `psycopg`) are added to `requirements.txt`, which that workflow
already installs, so the same job still lints and tests the app.

## Demonstrating a successful run (TC-CI-01)

Open any pull request against `main` and look at the "Checks" section —
`Lint and Test` should show a green check. `gh pr checks <number>` from the
CLI shows the same thing. PR #1 (backend foundation) is the first example
of this in the repo's history.

## Demonstrating an intentional failure (TC-CI-02)

Do this on a disposable branch, never on `main`:

```bash
git checkout -b demo/ci-failure
```

Then break something on purpose — e.g. add `assert False` to any test file,
or introduce an unused import (`import os` with no use) to trigger Ruff —
and push:

```bash
git add -A
git commit -m "Demo: intentional CI failure for TC-CI-02"
git push -u origin demo/ci-failure
```

Open a PR from `demo/ci-failure` into `main`. The `Lint and Test` check
will show a red ✗, and GitHub will refuse to let the PR merge if branch
protection requires passing checks. Capture a screenshot of the failed
check for the test evidence, then close the PR without merging and delete
the branch — don't merge the deliberately broken commit.

## Branch protection (recommended, needs a repo owner)

Settings → Branches → add a protection rule for `main` requiring the
`Lint and Test` check to pass before merging, and requiring at least one
approving review. This is what makes "repository owners must review and
merge pull requests" (section 2 of the brief) actually enforced by GitHub
rather than just a team agreement.

## Recovery if the pipeline itself breaks (not the app)

If `ci.yml` stops running at all (not just failing): check the Actions tab
for a workflow-syntax error first (GitHub shows these distinctly from test
failures). If dependency installation starts failing on a previously-green
commit, suspect an upstream package release — pin the exact version in
`requirements.txt` that was last known-good and re-run.
