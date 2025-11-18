from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class BoardCreate(BaseModel):
    name: str
    description: str | None = None
    color: Optional[str] = Field(None, max_length=50)
    
    
class BoardUpdate(BaseModel):
    name: str
    description: str | None = None
    color: Optional[str] = Field(None, max_length=50)

class BoardResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    color: Optional[str] = Field(None, max_length=50)
    
    class Config:
        from_attributes = True
        
class BoardOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    color: Optional[str] = None
    project_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


