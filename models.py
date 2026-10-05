
from sqlalchemy import Column, Integer, Float, String, JSON, DateTime
from sqlalchemy.sql import func
from database import Base


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    risk_score = Column(Float, nullable=False)
    risk_level = Column(String, nullable=False)
    category_scores = Column(JSON, nullable=False)
    recommendations = Column(JSON, nullable=False)
    answers = Column(JSON, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )