from pydantic import BaseModel
from typing import Optional

class BoardCreate(BaseModel):
    name: str
    description: str | None = None

class BoardResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    
    class Config:
        from_attributes = True


