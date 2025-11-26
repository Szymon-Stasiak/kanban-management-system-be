from pydantic import BaseModel, validator
from typing import Optional, Literal
from datetime import datetime

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    position: Optional[int] = None 
    column_id: int
    completed: Optional[bool] = False
    priority: Optional[Literal["low", "medium", "high"]] = "medium"

    due_date: datetime
    # due_date: Optional[datetime] = datetime.now() \\Optional
    
class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    position: Optional[int] = None 
    column_id: Optional[int] = None
    completed: Optional[bool] = None
    priority: Optional[Literal["low", "medium", "high"]] = None

    due_date: Optional[datetime] = None
    
class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    position: Optional[int] = None 
    column_id: int
    completed: bool
    priority: str

    due_date: datetime
    # due_date: Optional[datetime] \\Optional version

    class Config:
        from_attributes = True
    
class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    position: Optional[int] = None 
    column_id: int
    completed: bool
    priority: str

    due_date: datetime
    # due_date: Optional[datetime] \\Optional version

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


