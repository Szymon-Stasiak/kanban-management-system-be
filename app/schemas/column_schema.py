from pydantic import BaseModel
from typing import Optional

class ColumnCreate(BaseModel):
    name: str
    position: Optional[int] = None 
    board_id: int

class ColumnOut(ColumnCreate):
    id: int

    class Config:
        from_attributes = True
