
from sqlalchemy import Column, String, Text, Boolean, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.database import Base
import uuid


class Project(Base):
	__tablename__ = "projects"
	project_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
	name = Column(String(255), nullable=False)
	description = Column(Text)
	color = Column(String(50))
	archived = Column(Boolean, nullable=False, default=False)
	created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
	updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
