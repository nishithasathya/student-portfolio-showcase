from app.extensions import db


class Skill(db.Model):
    __tablename__ = "skills"

    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(
        db.Integer, db.ForeignKey("portfolios.id"), nullable=False, index=True
    )
    name = db.Column(db.String(80), nullable=False)
    category = db.Column(db.String(80))
    proficiency = db.Column(db.String(40))

    portfolio = db.relationship("Portfolio", back_populates="skills")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "proficiency": self.proficiency,
        }
