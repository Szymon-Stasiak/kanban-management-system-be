from sqlalchemy import Column, String, TIMESTAMP
from sqlalchemy.sql import func
from app.db.database import Base


class Token(Base):
    __tablename__ = "revoked_tokens"
    token = Column(String(255), primary_key=True)
    revoked_at = Column(TIMESTAMP, server_default=func.now())
    valid_until = Column(TIMESTAMP, nullable=False)
