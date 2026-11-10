# API Contract — Student Portfolio Showcase

This is the binding contract between the backend (`feature/backend-foundation`),
the frontend (`feature/frontend-development`) and the test suite
(`feature/security-testing`). Routes, field names and status codes here are
final for Sprint 1 — do not invent new endpoint names in the frontend or
tests. Any change to this file must be agreed by the owning branches before
it is merged.

All request/response bodies are JSON (`Content-Type: application/json`)
except where noted. Authentication is session-cookie based (Flask-Login):
after `/auth/login` or `/auth/register`, the browser must send the session
cookie on every subsequent request (`fetch(url, { credentials: "include" })`).

## Status codes

| Code | Meaning |
|------|---------|
| 200  | Success (read/update) |
| 201  | Resource created |
| 204  | Success, no body (delete) |
| 400  | Validation error (`{"error": "..."}`) |
| 401  | Not authenticated |
| 403  | Authenticated, but not the owner of this resource |
| 404  | Resource not found (also used for unpublished portfolios, to avoid leaking existence) |
| 409  | Conflict (e.g. duplicate email) |

## Endpoints

### `GET /`
Public. Landing/status payload: `{"message": "...", "status": "running"}`.

### `GET /health`
Public. `{"status": "healthy"}`, HTTP 200.

### `POST /auth/register`
Public.
- Request: `{"email": str, "password": str (>=8 chars), "display_name": str}`
- Response `201`: `{"id": int, "email": str, "portfolio_slug": str}`
- A portfolio is auto-created for the new user; `portfolio_slug` is derived
  from `display_name` and is guaranteed unique.
- Errors: `400` invalid email/password/display_name, `409` email already registered.

### `POST /auth/login`
Public.
- Request: `{"email": str, "password": str}`
- Response `200`: `{"id": int, "email": str}`
- Errors: `401` invalid email or password (generic message, does not reveal which field was wrong).

### `POST /auth/logout`
Requires authentication.
- Response `200`: `{"message": "Logged out."}`

### `GET /auth/me`
Requires authentication.
- Response `200`: `{"id": int, "email": str}`

### `GET /portfolio`
Requires authentication. Returns the caller's own portfolio (owner view,
includes `id` and `is_published`).
- Response `200`: see "Portfolio object (owner view)" below.

### `GET /portfolio/profile`
Requires authentication.
- Response `200`: `{"display_name": str, "headline": str|null, "bio": str|null}`

### `PUT /portfolio/profile`
Requires authentication. Partial update — only send fields you want to change.
- Request: `{"display_name"?: str, "headline"?: str, "bio"?: str}`
- Response `200`: owner-view portfolio object.

### `POST /portfolio/publish`
Requires authentication.
- Request: `{"is_published": bool}`
- Response `200`: `{"slug": str, "is_published": bool}`

### Skills — `POST /portfolio/skills`, `PUT /portfolio/skills/<id>`, `DELETE /portfolio/skills/<id>`
Requires authentication; `<id>` must belong to the caller's own portfolio
(otherwise `403`).
- Create request: `{"name": str, "category"?: str, "proficiency"?: str}`
- Update request: any subset of the same fields.
- Skill object: `{"id": int, "name": str, "category": str|null, "proficiency": str|null}`
- Create → `201` + skill object. Update → `200` + skill object. Delete → `204`.

### Projects — `POST /portfolio/projects`, `PUT /portfolio/projects/<id>`, `DELETE /portfolio/projects/<id>`
Same auth/ownership rules as skills.
- Create request: `{"title": str, "description"?: str, "technologies"?: str, "repo_url"?: str (http/https), "demo_url"?: str (http/https)}`
- Project object: `{"id": int, "title": str, "description": str|null, "technologies": str|null, "repo_url": str|null, "demo_url": str|null}`

### Achievements — `POST /portfolio/achievements`, `PUT /portfolio/achievements/<id>`, `DELETE /portfolio/achievements/<id>`
Same auth/ownership rules as skills. Covers both achievements and
certifications (distinguished by `type`).
- Create request: `{"title": str, "issuer"?: str, "awarded_on"?: "YYYY-MM-DD", "credential_url"?: str (http/https), "type"?: "achievement"|"certification"}`
- Achievement object: `{"id": int, "title": str, "issuer": str|null, "awarded_on": "YYYY-MM-DD"|null, "credential_url": str|null, "type": str}`

### `GET /p/<slug>`
Public. Returns the published portfolio for `slug`, or `404` if the slug
does not exist **or** exists but is unpublished (both look identical to a
visitor, by design — see SRS SPS-FR-016).
- Response `200`: "Portfolio object (public view)" below.

## Portfolio object (public view)

```json
{
  "slug": "ada-owner",
  "display_name": "Ada Owner",
  "headline": "AI/ML student",
  "bio": "...",
  "skills": [ { "id": 1, "name": "Python", "category": null, "proficiency": "advanced" } ],
  "projects": [ { "id": 1, "title": "...", "description": "...", "technologies": "...", "repo_url": "...", "demo_url": "..." } ],
  "achievements": [ { "id": 1, "title": "...", "issuer": "...", "awarded_on": "2026-05-01", "credential_url": "...", "type": "achievement" } ]
}
```

## Portfolio object (owner view)

Same as the public view, plus `"id": int` and `"is_published": bool`.
