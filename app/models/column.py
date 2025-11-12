# models/column.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.database import Base

class ColumnModel(Base): 
    __tablename__ = "columns"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    position = Column(Integer, nullable=False, default=0)  

    # Link to Board
    board_id = Column(Integer, ForeignKey("boards.id"), nullable=False)

    # Relationship with Board
    board = relationship("Board", back_populates="columns")

    # Placeholder for tasks (will add later)
    # tasks = relationship("Task", back_populates="column", cascade="all, delete-orphan")
