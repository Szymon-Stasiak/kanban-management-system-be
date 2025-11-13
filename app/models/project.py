from sqlalchemy import Column, String, Text, TIMESTAMP, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.database import Base
import uuid


class Project(Base):
    __tablename__ = "projects"

    project_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    public_project_id = Column(UUID(as_uuid=True), unique=True, default=uuid.uuid4)

    name = Column(String(150), nullable=False)
    description = Column(Text)
    color = Column(String(50))

    status = Column(
        String(20),
        nullable=False,
        default="active",
    )

    owner_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
    )

    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    archived_at = Column(TIMESTAMP)

    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'archived')",
            name="projects_status_check"
        ),
    )
