# Final Integration Test Summary & Evaluation Report

**Build under test:** `main` @ `642eea2` ("Record live Render deployment
URL in README"), verified 2026-11-12.
**All four feature branches are merged:** backend (#1), frontend (#19),
CI/CD and deployment (#20, #22), security and testing (#21).

This report follows the STP's own deliverable list (§8): test execution
results, requirement traceability, CI evidence, and an honest account of
what is *not* covered — a feature not implemented or not in scope is
marked not applicable, not claimed as passed.

## 1. Automated test results

```
58 passed in 3.55s
ruff check .  →  All checks passed!
```

Run fresh against a clean clone of `main` on 2026-11-12, not inherited
from an earlier branch. Breakdown by file:

| File | Tests | Focus |
|---|---|---|
| `test_app.py` | 2 | App factory smoke test, health endpoint |
| `test_backend_foundation.py` | 14 | Registration, login, profile, skills/projects/achievements CRUD, publish/unpublish, public view |
| `test_access_control.py` | 18 | Every protected endpoint requires auth (15 parametrized cases); cross-user 403 on projects and achievements; unpublished-portfolio 404 |
| `test_security.py` | 5 | Password hashing, session cookie hardening, error-response hygiene, generic invalid-login message, logout invalidation |
| `test_validators.py` | 14 | Every validator function, valid and invalid input, including rejection of `javascript:` URLs |
| `test_persistence.py` | 1 | Data survives a genuine two-process application restart |
| **Total** | **58** | |

No test is skipped, xfailed, or marked not-run — every collected test
executes and passes.

## 2. Requirement traceability (STP §13)

| Test ID (STP) | SRS requirement | Covered by | Result |
|---|---|---|---|
| TC-OPS-01 | SPS-FR-020 / AT-002 | `test_health_endpoint` | Pass |
| TC-AUTH-01 | SPS-FR-001 | `test_register_creates_account_and_portfolio`, `test_register_rejects_duplicate_email`, `test_register_rejects_invalid_email`, `test_register_rejects_short_password` | Pass |
| TC-AUTH-02 | SPS-FR-002 | `test_login_with_valid_credentials` | Pass |
| TC-AUTH-03 | SPS-FR-003 | `test_login_rejects_wrong_password`, `test_invalid_login_error_does_not_reveal_which_field_was_wrong` | Pass |
| TC-AUTH-04 | SPS-FR-004 | `test_logout_then_protected_route_requires_auth`, `test_logout_invalidates_session_immediately` | Pass |
| TC-PROF-01/02/03 | SPS-FR-005–007 | `test_profile_create_update_and_view` | Pass |
| TC-SKILL-01/02 | SPS-FR-008/009 | `test_skill_add_edit_remove` | Pass |
| TC-PROJ-01/02/03 | SPS-FR-010–012 | `test_project_add_edit_remove`, `test_project_rejects_invalid_url` | Pass |
| TC-ACH-01 | SPS-FR-013 | `test_achievement_add_edit_remove` | Pass |
| TC-PUB-01/02 | SPS-FR-014/015 | `test_publish_and_public_view` | Pass |
| TC-PUB-03 | SPS-FR-016 | `test_unpublished_portfolio_is_not_visible`, `test_cross_user_cannot_view_unpublished_profile_via_its_own_slug_guess` | Pass |
| TC-VAL-01 | SPS-FR-017 | All of `test_validators.py`, plus `test_register_rejects_*` | Pass |
| TC-ERR-01 | SPS-FR-018 | `test_unknown_slug_returns_404`, `test_not_found_response_has_no_stack_trace` | Pass |
| TC-DB-01 | SPS-FR-019 | `test_data_persists_across_application_restart` | Pass |
| TC-CI-01 | SPS-FR-021 | 13 GitHub Actions runs, 100% success (see §3) | Pass |
| TC-CI-02 | SPS-FR-022 | — | **Not run** (see §4) |
| TC-SEC-01 | SPS-SEC-002 | `test_cross_user_cannot_edit_another_owners_skill`, `test_cross_user_cannot_edit_or_delete_project`, `test_cross_user_cannot_edit_or_delete_achievement` | Pass |
| TC-SEC-02 | SPS-SEC-005/006 | `test_not_found_response_has_no_stack_trace`, `test_password_is_hashed_not_plaintext`, `test_session_cookies_are_hardened`, plus a manual header check against the live deployment | Pass |

Quality-attribute rows (SPS-NFR-001–008 — performance, usability,
compatibility, accessibility, portability) were reviewed manually during
development and integration (browser walkthroughs, responsive-layout
checks down to ~600px) rather than through dedicated automated tooling.
See §4 for exactly what that does and doesn't cover.

## 3. CI/CD evidence

13 GitHub Actions runs on this repository, **100% success**, across every
merge (`feature/backend-foundation`, `feature/frontend-development`,
`feature/cicd-deployment` ×2, `feature/security-testing`) and every push
to `main`. Branch protection on `main` now requires the `Lint and Test`
check and 1 approving review before merge (configured 2026-11-12).

## 4. Live deployment verification

Verified directly against https://student-portfolio-showcase.onrender.com
on 2026-11-12 (full results on GitHub issue #15): health check, register,
add-skill-and-persist, publish, public view, unpublish → 404, and
logout → 401 on the next request all pass against the real production
service (PostgreSQL-backed, not local SQLite).

## 5. Known limitations (documented honestly, not hidden)

- **No automated frontend tests.** All 58 tests exercise the backend API
  directly; none drive the rendered pages or their JavaScript. The
  frontend was verified by manual browser walkthroughs during
  integration (register → dashboard → editor → publish → public view),
  not by an automated suite. A stored-XSS check was done manually
  (submitting `<img src=x onerror=...>` as a project title and
  confirming it rendered inert) rather than via a repeatable test.
- **TC-CI-02 (intentional CI failure) has not actually been run.**
  `docs/CICD_EXPLANATION.md` documents the exact steps to demonstrate it
  on a disposable branch, but no one has executed them yet — this is
  prepared, not evidenced.
- **No rate limiting or brute-force protection on login.** Not required
  by the SRS, but worth naming as a boundary of what was built.
- **Branch protection has `enforce_admins: false`** — the repository
  owner can bypass the required check/review. Deliberate (so a fix isn't
  blocked right before a deadline), but it means the rule isn't absolute.
- **No file/image upload support.** The SAD lists this as something that
  "may be added if required" (§10.4) — it was not required, and wasn't
  built.
- **Performance, accessibility and cross-browser compatibility
  (SPS-NFR-001, 005, 006) were reviewed manually, not automated.** No
  load test, no automated accessibility audit (e.g. axe-core), and
  compatibility was only exercised in one browser engine during
  development, not independently verified in a second one.
- **A portfolio is strictly 1:1 with a user** (per the SAD's data
  design) — there is no multi-portfolio-per-user feature, which was
  never requested but is worth stating as a fixed design boundary.

## 6. Exit criteria (STP §5.2)

| Criterion | Status |
|---|---|
| All in-scope test cases have a recorded status | Met — 58/58, all recorded above |
| No unresolved critical/high defect without documented acceptance | Met — no open defects found during this integration pass |
| Core acceptance criteria met or deviations documented | Met — deviations are the Achievement/Certification entity merge (SAD §10.6-permitted) and the SQLite→Postgres production swap (`docs/DEPLOYMENT.md`) |
| Lint and automated tests pass on candidate main-branch commit | Met — verified fresh on `642eea2` |
| Test summary, failures, limitations and evidence recorded | Met — this document |

No blocking defects were found. The limitations in §5 are scope
boundaries, not failures of what was attempted.
