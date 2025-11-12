from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.board import Board
from app.schemas.board_schema import BoardCreate
# from app.models.project import Project

router = APIRouter()

@router.post("/create")
def create_board(board: BoardCreate, db: Session = Depends(get_db)):
    
    # project = db.query(Project).filter(Project.id == board.project_id).first()
    # if not project:
        # raise HTTPException(status_code=404, detail="Project not found")
    
    new_board = Board(
        name=board.name,
        description=board.description,
        project_id=None  # temporary, no project for now
    )
    db.add(new_board)
    db.commit()
    db.refresh(new_board)
    return new_board

@router.get("/")
def get_boards(db: Session = Depends(get_db)):
    boards = db.query(Board).all()
    return boards

# Delete a board
@router.delete("/{board_id}")
def delete_column(board_id: int, db: Session = Depends(get_db)):
    db_board = db.query(Board).filter(Board.id == board_id).first()
    if not db_board:
        raise HTTPException(status_code=404, detail="Board not found")

    db.delete(db_board)
    db.commit()
    return {"message": "Board deleted successfully"}

