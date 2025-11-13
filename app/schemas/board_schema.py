from pydantic import BaseModel
from typing import Optional

class BoardCreate(BaseModel):
    name: str
    description: str | None = None
    project_id: int


