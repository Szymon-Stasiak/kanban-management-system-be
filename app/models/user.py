from sqlalchemy import Column, String, Boolean, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID, CITEXT
from sqlalchemy.sql import func
from app.db.database import Base
import uuid
from app.constant import ACTIVE, USER_ROLE

class User(Base):
    __tablename__ = "users"
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    email_verified = Column(Boolean, default=False)
    verification_token = Column(String(255))
    reset_token = Column(String(255))
    reset_token_expires_at = Column(TIMESTAMP)
    name = Column(String(100))
    surname = Column(String(100))
    bio = Column(Text)
    avatar_url = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    role = Column(String(50), default=USER_ROLE)
    status = Column(String(50), default=ACTIVE)



