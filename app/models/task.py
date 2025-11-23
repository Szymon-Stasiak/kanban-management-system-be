from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, func
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.database import Base

class Task(Base): 
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False, index=True)
    description = Column(Text, nullable=True) 
    completed = Column(Boolean, default=False, nullable=False)
    priority = Column(String(20), default="medium", nullable=False)
    # Adding due date
    # due_date = Column(DateTime, default=datetime.now(timezone=True), nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=False)
    column_id = Column(Integer, ForeignKey("columns.id", ondelete="CASCADE"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship 
    column = relationship("ColumnModel", back_populates="tasks")
