from datetime import datetime, timezone

from app.extensions import db


class Portfolio(db.Model):
    __tablename__ = "portfolios"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False
    )
    slug = db.Column(db.String(140), unique=True, nullable=False, index=True)
    display_name = db.Column(db.String(120), nullable=False)
    headline = db.Column(db.String(200))
    bio = db.Column(db.Text)
    is_published = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user = db.relationship("User", back_populates="portfolio")
    skills = db.relationship(
        "Skill",
        back_populates="portfolio",
        cascade="all, delete-orphan",
        order_by="Skill.id",
    )
    projects = db.relationship(
        "Project",
        back_populates="portfolio",
        cascade="all, delete-orphan",
        order_by="Project.id",
    )
    achievements = db.relationship(
        "Achievement",
        back_populates="portfolio",
        cascade="all, delete-orphan",
        order_by="Achievement.id",
    )

    def to_public_dict(self):
        return {
            "slug": self.slug,
            "display_name": self.display_name,
            "headline": self.headline,
            "bio": self.bio,
            "skills": [s.to_dict() for s in self.skills],
            "projects": [p.to_dict() for p in self.projects],
            "achievements": [a.to_dict() for a in self.achievements],
        }

    def to_owner_dict(self):
        data = self.to_public_dict()
        data.update({"id": self.id, "is_published": self.is_published})
        return data
