from pydantic import BaseModel, validator
from typing import Optional, Literal
from datetime import datetime

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    column_id: int
    completed: Optional[bool] = False
    priority: Optional[Literal["low", "medium", "high"]] = "medium"
    
class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    column_id: Optional[int] = None
    completed: Optional[bool] = None
    priority: Optional[Literal["low", "medium", "high"]] = None
    
class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    column_id: int
    completed: bool
    priority: str

    class Config:
        from_attributes = True
    
class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    column_id: int
    completed: bool
    priority: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


