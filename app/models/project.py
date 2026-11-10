from app.extensions import db


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(
        db.Integer, db.ForeignKey("portfolios.id"), nullable=False, index=True
    )
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    technologies = db.Column(db.String(300))
    repo_url = db.Column(db.String(300))
    demo_url = db.Column(db.String(300))

    portfolio = db.relationship("Portfolio", back_populates="projects")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "technologies": self.technologies,
            "repo_url": self.repo_url,
            "demo_url": self.demo_url,
        }
