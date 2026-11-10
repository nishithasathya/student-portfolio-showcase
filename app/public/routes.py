from flask import Blueprint, jsonify

from app.errors import NotFoundError
from app.models import Portfolio

bp = Blueprint("public", __name__)


@bp.get("/p/<slug>")
def view_public_portfolio(slug):
    # SPS-FR-016: an unpublished or missing slug must look identical to a visitor.
    portfolio = Portfolio.query.filter_by(slug=slug, is_published=True).first()
    if portfolio is None:
        raise NotFoundError("Portfolio not found or not published.")
    return jsonify(portfolio.to_public_dict()), 200
