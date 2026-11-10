/**
 * Thin wrapper around fetch() matching docs/API_CONTRACT.md exactly.
 * Every call sends cookies (credentials: "include") so the Flask-Login
 * session survives across requests.
 */

async function apiRequest(path, { method = "GET", body } = {}) {
  const response = await fetch(path, {
    method,
    headers: body !== undefined ? { "Content-Type": "application/json" } : {},
    credentials: "include",
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  let data = null;
  if (response.status !== 204) {
    data = await response.json().catch(() => null);
  }

  if (!response.ok) {
    const message = (data && data.error) || `Request failed (${response.status})`;
    const error = new Error(message);
    error.status = response.status;
    throw error;
  }

  return data;
}

const api = {
  register: (payload) => apiRequest("/auth/register", { method: "POST", body: payload }),
  login: (payload) => apiRequest("/auth/login", { method: "POST", body: payload }),
  logout: () => apiRequest("/auth/logout", { method: "POST" }),
  me: () => apiRequest("/auth/me"),

  getPortfolio: () => apiRequest("/portfolio"),
  getProfile: () => apiRequest("/portfolio/profile"),
  updateProfile: (payload) => apiRequest("/portfolio/profile", { method: "PUT", body: payload }),
  setPublishState: (isPublished) =>
    apiRequest("/portfolio/publish", { method: "POST", body: { is_published: isPublished } }),

  addSkill: (payload) => apiRequest("/portfolio/skills", { method: "POST", body: payload }),
  updateSkill: (id, payload) =>
    apiRequest(`/portfolio/skills/${id}`, { method: "PUT", body: payload }),
  deleteSkill: (id) => apiRequest(`/portfolio/skills/${id}`, { method: "DELETE" }),

  addProject: (payload) => apiRequest("/portfolio/projects", { method: "POST", body: payload }),
  updateProject: (id, payload) =>
    apiRequest(`/portfolio/projects/${id}`, { method: "PUT", body: payload }),
  deleteProject: (id) => apiRequest(`/portfolio/projects/${id}`, { method: "DELETE" }),

  addAchievement: (payload) =>
    apiRequest("/portfolio/achievements", { method: "POST", body: payload }),
  updateAchievement: (id, payload) =>
    apiRequest(`/portfolio/achievements/${id}`, { method: "PUT", body: payload }),
  deleteAchievement: (id) => apiRequest(`/portfolio/achievements/${id}`, { method: "DELETE" }),

  getPublicPortfolio: (slug) => apiRequest(`/p/${encodeURIComponent(slug)}`),
};
