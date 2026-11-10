/**
 * Page logic for all templates. Each init function bails out immediately
 * if its page's root element isn't present, so one file can serve every
 * page without errors.
 */

function escapeHtml(value) {
  const div = document.createElement("div");
  div.textContent = value === null || value === undefined ? "" : String(value);
  return div.innerHTML;
}

function showMessage(el, text, type = "error") {
  if (!el) return;
  el.textContent = text;
  el.className = `message message-${type}`;
  el.hidden = false;
}

function clearMessage(el) {
  if (!el) return;
  el.hidden = true;
  el.textContent = "";
}

document.addEventListener("DOMContentLoaded", () => {
  initRegisterForm();
  initLoginForm();
  initLogoutButton();
  initDashboard();
  initPortfolioEditor();
  initPublicPortfolio();
});

function initRegisterForm() {
  const form = document.getElementById("register-form");
  if (!form) return;
  const messageEl = document.getElementById("register-message");

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearMessage(messageEl);
    const formData = new FormData(form);

    try {
      await api.register({
        email: formData.get("email"),
        password: formData.get("password"),
        display_name: formData.get("display_name"),
      });
      window.location.href = "/dashboard";
    } catch (err) {
      showMessage(messageEl, err.message, "error");
    }
  });
}

function initLoginForm() {
  const form = document.getElementById("login-form");
  if (!form) return;
  const messageEl = document.getElementById("login-message");

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearMessage(messageEl);
    const formData = new FormData(form);

    try {
      await api.login({ email: formData.get("email"), password: formData.get("password") });
      window.location.href = "/dashboard";
    } catch (err) {
      showMessage(messageEl, err.message, "error");
    }
  });
}

function initLogoutButton() {
  const button = document.getElementById("logout-button");
  if (!button) return;

  button.addEventListener("click", async () => {
    try {
      await api.logout();
    } finally {
      window.location.href = "/login";
    }
  });
}


async function initDashboard() {
  const container = document.getElementById("dashboard-summary");
  if (!container) return;

  try {
    const portfolio = await api.getPortfolio();

    const skillCount = portfolio.skills.length;
    const projectCount = portfolio.projects.length;
    const achievementCount = portfolio.achievements.length;

    container.innerHTML = `
      <div class="dashboard-profile">
        <div>
          <h2>${escapeHtml(portfolio.display_name)}</h2>
          <p>${escapeHtml(portfolio.headline || "Add a headline to introduce yourself.")}</p>
        </div>

        <span class="status-badge ${portfolio.is_published ? "status-published" : "status-private"}">
          ${portfolio.is_published ? "Published" : "Private"}
        </span>
      </div>

      <div class="dashboard-stats">
        <div class="stat-card">
          <span class="stat-number">${skillCount}</span>
          <span class="stat-label">Skills</span>
        </div>

        <div class="stat-card">
          <span class="stat-number">${projectCount}</span>
          <span class="stat-label">Projects</span>
        </div>

        <div class="stat-card">
          <span class="stat-number">${achievementCount}</span>
          <span class="stat-label">Achievements</span>
        </div>
      </div>

      <div class="dashboard-public-link">
        <div>
          <h3>Your public portfolio</h3>
          <p>Share your work with others using this link.</p>
          <a href="/u/${encodeURIComponent(portfolio.slug)}">
            /u/${escapeHtml(portfolio.slug)}
          </a>
        </div>
      </div>
    `;
  } catch (err) {
    window.location.href = "/login";
  }
}

async function initPortfolioEditor() {
  const root = document.getElementById("portfolio-editor");
  if (!root) return;

  const messageEl = document.getElementById("editor-message");
  let portfolio;

  try {
    portfolio = await api.getPortfolio();
  } catch (err) {
    window.location.href = "/login";
    return;
  }

  document.getElementById("profile-display-name").value = portfolio.display_name || "";
  document.getElementById("profile-headline").value = portfolio.headline || "";
  document.getElementById("profile-bio").value = portfolio.bio || "";

  document.getElementById("profile-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    clearMessage(messageEl);
    try {
      await api.updateProfile({
        display_name: document.getElementById("profile-display-name").value,
        headline: document.getElementById("profile-headline").value,
        bio: document.getElementById("profile-bio").value,
      });
      showMessage(messageEl, "Profile saved.", "success");
    } catch (err) {
      showMessage(messageEl, err.message, "error");
    }
  });

  const publishToggle = document.getElementById("publish-toggle");
  const publicLink = document.getElementById("public-link");
  publishToggle.checked = portfolio.is_published;
  publicLink.href = `/u/${encodeURIComponent(portfolio.slug)}`;
  publicLink.textContent = `/u/${portfolio.slug}`;

  publishToggle.addEventListener("change", async (event) => {
    const nextState = event.target.checked;
    try {
      await api.setPublishState(nextState);
      showMessage(messageEl, nextState ? "Portfolio published." : "Portfolio unpublished.", "success");
    } catch (err) {
      event.target.checked = !nextState;
      showMessage(messageEl, err.message, "error");
    }
  });

  initSkillsSection(portfolio.skills, messageEl);
  initProjectsSection(portfolio.projects, messageEl);
  initAchievementsSection(portfolio.achievements, messageEl);
}

function initSkillsSection(skills, messageEl) {
  const list = document.getElementById("skills-list");
  const form = document.getElementById("skill-form");

  function buildRow(skill) {
    const li = document.createElement("li");
    li.className = "entry-row";
    const label = skill.proficiency ? `${skill.name} — ${skill.proficiency}` : skill.name;
    li.innerHTML = `
      <span>${escapeHtml(label)}</span>
      <button type="button" class="remove-button">Remove</button>
    `;
    li.querySelector("button").addEventListener("click", async () => {
      try {
        await api.deleteSkill(skill.id);
        li.remove();
      } catch (err) {
        showMessage(messageEl, err.message, "error");
      }
    });
    return li;
  }

  skills.forEach((skill) => list.appendChild(buildRow(skill)));

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearMessage(messageEl);
    try {
      const skill = await api.addSkill({
        name: form.elements["name"].value,
        category: form.elements["category"].value || undefined,
        proficiency: form.elements["proficiency"].value || undefined,
      });
      list.appendChild(buildRow(skill));
      form.reset();
    } catch (err) {
      showMessage(messageEl, err.message, "error");
    }
  });
}

function initProjectsSection(projects, messageEl) {
  const list = document.getElementById("projects-list");
  const form = document.getElementById("project-form");

  function buildRow(project) {
    const li = document.createElement("li");
    li.className = "entry-row";
    const repoLink = project.repo_url
      ? `<a href="${escapeHtml(project.repo_url)}" target="_blank" rel="noopener">Repo</a>`
      : "";
    li.innerHTML = `
      <div>
        <strong>${escapeHtml(project.title)}</strong>
        <p>${escapeHtml(project.description || "")}</p>
        ${repoLink}
      </div>
      <button type="button" class="remove-button">Remove</button>
    `;
    li.querySelector("button").addEventListener("click", async () => {
      try {
        await api.deleteProject(project.id);
        li.remove();
      } catch (err) {
        showMessage(messageEl, err.message, "error");
      }
    });
    return li;
  }

  projects.forEach((project) => list.appendChild(buildRow(project)));

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearMessage(messageEl);
    try {
      const project = await api.addProject({
        title: form.elements["title"].value,
        description: form.elements["description"].value || undefined,
        technologies: form.elements["technologies"].value || undefined,
        repo_url: form.elements["repo_url"].value || undefined,
        demo_url: form.elements["demo_url"].value || undefined,
      });
      list.appendChild(buildRow(project));
      form.reset();
    } catch (err) {
      showMessage(messageEl, err.message, "error");
    }
  });
}

function initAchievementsSection(achievements, messageEl) {
  const list = document.getElementById("achievements-list");
  const form = document.getElementById("achievement-form");

  function buildRow(achievement) {
    const li = document.createElement("li");
    li.className = "entry-row";
    li.innerHTML = `
      <div>
        <strong>${escapeHtml(achievement.title)}</strong> (${escapeHtml(achievement.type)})
        <p>${escapeHtml(achievement.issuer || "")} ${escapeHtml(achievement.awarded_on || "")}</p>
      </div>
      <button type="button" class="remove-button">Remove</button>
    `;
    li.querySelector("button").addEventListener("click", async () => {
      try {
        await api.deleteAchievement(achievement.id);
        li.remove();
      } catch (err) {
        showMessage(messageEl, err.message, "error");
      }
    });
    return li;
  }

  achievements.forEach((achievement) => list.appendChild(buildRow(achievement)));

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearMessage(messageEl);
    try {
      const achievement = await api.addAchievement({
        title: form.elements["title"].value,
        issuer: form.elements["issuer"].value || undefined,
        awarded_on: form.elements["awarded_on"].value || undefined,
        credential_url: form.elements["credential_url"].value || undefined,
        type: form.elements["type"].value || "achievement",
      });
      list.appendChild(buildRow(achievement));
      form.reset();
    } catch (err) {
      showMessage(messageEl, err.message, "error");
    }
  });
}

async function initPublicPortfolio() {
  const root = document.getElementById("public-portfolio");
  if (!root) return;

  const slug = root.dataset.slug;

  try {
    const portfolio = await api.getPublicPortfolio(slug);

    document.getElementById("public-display-name").textContent = portfolio.display_name;
    document.getElementById("public-headline").textContent = portfolio.headline || "";
    document.getElementById("public-bio").textContent = portfolio.bio || "";

    document.getElementById("public-skills").innerHTML = portfolio.skills
      .map((s) => `<li>${escapeHtml(s.proficiency ? `${s.name} — ${s.proficiency}` : s.name)}</li>`)
      .join("");

    document.getElementById("public-projects").innerHTML = portfolio.projects
      .map((p) => {
        const repoLink = p.repo_url
          ? `<a href="${escapeHtml(p.repo_url)}" target="_blank" rel="noopener">Repo</a>`
          : "";
        return `<li><strong>${escapeHtml(p.title)}</strong><p>${escapeHtml(
          p.description || ""
        )}</p>${repoLink}</li>`;
      })
      .join("");

    document.getElementById("public-achievements").innerHTML = portfolio.achievements
      .map(
        (a) =>
          `<li><strong>${escapeHtml(a.title)}</strong> — ${escapeHtml(a.issuer || "")} ${escapeHtml(
            a.awarded_on || ""
          )}</li>`
      )
      .join("");
  } catch (err) {
    document.getElementById("public-display-name").textContent = "Portfolio not available";
    root.querySelectorAll("ul, p:not(:first-of-type)").forEach((el) => el.remove());
  }
}
