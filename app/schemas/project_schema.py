from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    color: Optional[str] = None
    archived: Optional[bool] = False


class ProjectOut(BaseModel):
    project_id: UUID
    name: str
    description: Optional[str] = None
    color: Optional[str] = None
    archived: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    archived: Optional[bool] = None
