from flask import Blueprint, render_template

bp = Blueprint("views", __name__)

# These routes only serve the page shell (HTML + CSS + JS). All data comes
# from the JSON API in docs/API_CONTRACT.md via client-side fetch calls —
# auth gating happens in the browser (an unauthenticated fetch gets a 401
# and main.js redirects to /login), so no portfolio data is rendered here.


@bp.get("/register")
def register_page():
    return render_template("register.html")


@bp.get("/login")
def login_page():
    return render_template("login.html")


@bp.get("/dashboard")
def dashboard_page():
    return render_template("dashboard.html")


@bp.get("/portfolio-editor")
def portfolio_editor_page():
    return render_template("portfolio.html")


@bp.get("/u/<slug>")
def public_portfolio_page(slug):
    return render_template("public_portfolio.html", slug=slug)
