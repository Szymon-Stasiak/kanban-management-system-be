from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.board import Board
from app.models.project import Project
from app.schemas.board_schema import BoardCreate
from app.routes.auth_routes import get_current_user

router = APIRouter()

@router.post("/create")
def create_board(board: BoardCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    
    project = (
        db.query(Project)
        .filter(Project.project_id == board.project_id, Project.owner_id == current_user.user_id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found or access denied")
    
    new_board = Board(
        name=board.name,
        description=board.description,
        project_id= project.project_id
    )
    db.add(new_board)
    db.commit()
    db.refresh(new_board)
    return new_board

@router.get("/")
def get_boards(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    boards = (
        db.query(Board)
        .join(Project)
        .filter(Project.owner_id == current_user.user_id)
        .all()
    )
    return boards

# Delete a board
@router.delete("/{board_id}")
def delete_board(board_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db_board = (
        db.query(Board)
        .join(Project)
        .filter(Board.id == board_id, Project.owner_id == current_user.user_id)
        .first()
    )
    if not db_board:
        raise HTTPException(status_code=404, detail="Board not found or access denied")

    db.delete(db_board)
    db.commit()
    return {"message": "Board deleted successfully"}

