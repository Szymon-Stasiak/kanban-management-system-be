from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from models.board import Board

app = FastAPI()

@app.post("/boards")
def create_board(name: str, description: str = None, db: Session = Depends(get_db)):
    new_board = Board(
        name=name,
        description=description,
        project_id=None  # temporary, no project for now
    )
    db.add(new_board)
    db.commit()
    db.refresh(new_board)
    return new_board

@app.get("/boards")
def get_boards(db: Session = Depends(get_db)):
    boards = db.query(Board).all()
    return boards

