from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.db.database import get_db
from app.models.project import Project
from app.schemas.project_schema import ProjectCreate, ProjectOut, ProjectUpdate
from app.services.jwt_service import get_current_user

router = APIRouter()

@router.post("/add", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    project: ProjectCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    new_project = Project(
        name=project.name,
        description=project.description,
        color=project.color,
        status=project.status or "active",
        owner_id=current_user.user_id,
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project


@router.get("/getall", response_model=List[ProjectOut])
def get_projects(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    projects = db.query(Project).filter(Project.owner_id == current_user.user_id).all()
    return projects


@router.get("/{public_project_id}", response_model=ProjectOut)
def get_project(
    public_project_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    project = (
        db.query(Project)
        .filter(Project.public_project_id == public_project_id, Project.owner_id == current_user.user_id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found or access denied")
    return project


@router.put("/update/{public_project_id}", response_model=ProjectOut)
def update_project(
    public_project_id: str,
    project_update: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    project = (
        db.query(Project)
        .filter(Project.public_project_id == public_project_id, Project.owner_id == current_user.user_id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found or access denied")

    if project_update.name is not None:
        project.name = project_update.name
    if project_update.description is not None:
        project.description = project_update.description
    if project_update.color is not None:
        project.color = project_update.color
    if project_update.status is not None:
        project.status = project_update.status
        if project.status == "archived":
            project.archived_at = func.now()
        else:
            project.archived_at = None

    db.commit()
    db.refresh(project)
    return project


@router.delete("/delete/{public_project_id}")
def delete_project(
    public_project_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    project = (
        db.query(Project)
        .filter(Project.public_project_id == public_project_id, Project.owner_id == current_user.user_id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found or access denied")

    db.delete(project)
    db.commit()
    return {"detail": f"Project '{project.name}' deleted successfully"}
