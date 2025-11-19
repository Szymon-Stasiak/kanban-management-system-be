from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    position: Optional[int] = None 
    column_id: int
    
class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    position: Optional[int] = None 
    column_id: Optional[int] = None
    
class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    position: Optional[int] = None 
    column_id: int

    class Config:
        from_attributes = True
    
class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    position: Optional[int] = None 
    column_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


