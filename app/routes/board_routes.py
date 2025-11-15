from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app.db.database import get_db
from app.models.board import Board
from app.models.project import Project
from app.schemas.board_schema import BoardCreate
from app.services.jwt_service import get_current_user

router = APIRouter()


# CREATE a board under a project (using public_project_id)
@router.post("/create/project/{public_project_id}")
def create_board(
    public_project_id: UUID,
    board: BoardCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    project = (
        db.query(Project)
        .filter(Project.public_project_id == public_project_id, Project.owner_id == current_user.user_id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found or access denied")
    
    new_board = Board(
        name=board.name,
        description=board.description,
        project_id=project.public_project_id
    )
    db.add(new_board)
    db.commit()
    db.refresh(new_board)
    return new_board

# GET all boards for a project
@router.get("/project/{public_project_id}")
def get_boards_for_project(
    public_project_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    project = (
        db.query(Project)
        .filter(Project.public_project_id == public_project_id, Project.owner_id == current_user.user_id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    boards = db.query(Board).filter(Board.project_id == project.public_project_id).all()
    return boards

@router.delete("/{board_id}/project/{public_project_id}")
def delete_board(
    board_id: int,
    public_project_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    project = db.query(Project).filter(
        Project.public_project_id == public_project_id,
        Project.owner_id == current_user.user_id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found or access denied")

    board = db.query(Board).filter(
        Board.id == board_id,
        Board.project_id == project.public_project_id
    ).first()

    if not board:
        raise HTTPException(status_code=404, detail="Board not found or access denied")

    db.delete(board)
    db.commit()
    return {"message": "Board deleted successfully"}
