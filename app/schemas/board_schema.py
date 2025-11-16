from pydantic import BaseModel, Field
from typing import Optional

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


