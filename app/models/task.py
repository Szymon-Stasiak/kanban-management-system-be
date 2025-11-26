from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.database import Base

class Task(Base): 
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False, index=True)
    description = Column(Text, nullable=True) 
    position = Column(Integer, nullable=False, default=0)  
    
    completed = Column(Boolean, default=False, nullable=False)
    priority = Column(String(20), default="medium", nullable=False)

    due_date = Column(DateTime(timezone=True), nullable=False)
    column_id = Column(Integer, ForeignKey("columns.id", ondelete="CASCADE"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship 
    column = relationship("ColumnModel", back_populates="tasks")
