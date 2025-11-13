from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class ProjectCreate(BaseModel):
    name: str = Field(..., max_length=150)
    description: Optional[str] = None
    color: Optional[str] = Field(None, max_length=50)
    status: Optional[str] = Field("active", pattern="^(active|archived)$")


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=150)
    description: Optional[str] = None
    color: Optional[str] = Field(None, max_length=50)
    status: Optional[str] = Field(None, pattern="^(active|archived)$")


class ProjectOut(BaseModel):
    public_project_id: UUID
    owner_id: UUID
    name: str
    description: Optional[str] = None
    color: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    archived_at: Optional[datetime] = None

    class Config:
        from_attributes = True
