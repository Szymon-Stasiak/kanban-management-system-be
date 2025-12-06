from typing import List, Optional
from io import BytesIO
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import func
from app.db.database import get_db
from app.models.project import Project
from app.models.board import Board
from app.models.column import ColumnModel
from app.models.task import Task
from app.schemas.project_schema import ProjectCreate, ProjectOut, ProjectUpdate
from app.services.jwt_service import get_current_user

from app.services.pdf_service import build_project_pdf
from app.services.csv_service import build_project_csv

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


@router.get("/pdf/{public_project_id}")
def generate_project_pdf(
    public_project_id: str,
    board_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Generate a PDF for the project containing all columns and tasks.
    """
    # Pobierz projekt z boardami, kolumnami i taskami
    project = (
        db.query(Project)
        .filter(Project.public_project_id == public_project_id, Project.owner_id == current_user.user_id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found or access denied")

    # Pobierz wszystkie boardy projektu wraz z kolumnami i taskami
    # If board_id provided, return only that board (if it belongs to the project)
    query = db.query(Board).options(joinedload(Board.columns).joinedload(ColumnModel.tasks))
    if board_id is not None:
        query = query.filter(Board.id == board_id, Board.project_id == project.public_project_id)
    else:
        query = query.filter(Board.project_id == project.public_project_id)
    boards = query.all()

    buffer = build_project_pdf(project, boards)

    filename = f"project_{project.name.replace(' ', '_')}.pdf"

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/csv/{public_project_id}")
def generate_project_csv(
    public_project_id: str,
    board_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Generate CSV for the project containing all columns and tasks.
    """
    project = (
        db.query(Project)
        .filter(Project.public_project_id == public_project_id, Project.owner_id == current_user.user_id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found or access denied")

    query = db.query(Board).options(joinedload(Board.columns).joinedload(ColumnModel.tasks))
    if board_id is not None:
        query = query.filter(Board.id == board_id, Board.project_id == project.public_project_id)
    else:
        query = query.filter(Board.project_id == project.public_project_id)
    boards = query.all()

    buffer = build_project_csv(project, boards)

    filename = f"project_{project.name.replace(' ', '_')}.csv"

    return StreamingResponse(
        buffer,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
