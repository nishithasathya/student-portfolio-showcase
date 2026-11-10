from app.extensions import db


class Achievement(db.Model):
    __tablename__ = "achievements"

    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(
        db.Integer, db.ForeignKey("portfolios.id"), nullable=False, index=True
    )
    title = db.Column(db.String(150), nullable=False)
    issuer = db.Column(db.String(150))
    awarded_on = db.Column(db.Date)
    credential_url = db.Column(db.String(300))
    # "achievement" or "certification" — SRS SPS-FR-013 treats both as one entity.
    type = db.Column(db.String(40), default="achievement", nullable=False)

    portfolio = db.relationship("Portfolio", back_populates="achievements")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "issuer": self.issuer,
            "awarded_on": self.awarded_on.isoformat() if self.awarded_on else None,
            "credential_url": self.credential_url,
            "type": self.type,
        }
