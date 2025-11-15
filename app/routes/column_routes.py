# app/routes/column_routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.column import ColumnModel
from app.models.board import Board
from app.models.project import Project
from app.schemas.column_schema import ColumnCreate, ColumnOut
from typing import List
from app.services.jwt_service import get_current_user

router = APIRouter()

# Create a column in a board
@router.post("/create", response_model=ColumnOut)
def create_column(column: ColumnCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    board = (
        db.query(Board)
        .join(Project)
        .filter(Board.id == column.board_id, Project.owner_id == current_user.user_id)
        .first()
    )
    if not board:
        raise HTTPException(status_code=404, detail="Board not found or access denied")

    new_column = ColumnModel(
        name=column.name,
        position=column.position,
        board_id=column.board_id
    )
    db.add(new_column)
    db.commit()
    db.refresh(new_column)
    return new_column

# Get all the column of that board
@router.get("/{board_id}", response_model=List[ColumnOut])
def get_columns_for_board(board_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    columns = (
        db.query(ColumnModel)
        .join(Board)
        .join(Project)
        .filter(ColumnModel.board_id == board_id, Project.owner_id == current_user.user_id)
        .all()
    )
    return columns


# Rename (update) a column
@router.put("/{column_id}", response_model=ColumnOut)
def update_column(column_id: int, column: ColumnCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db_column = (
        db.query(ColumnModel)
        .join(Board)
        .join(Project)
        .filter(ColumnModel.id == column_id, Project.owner_id == current_user.user_id)
        .first()
    )
    if not db_column:
        raise HTTPException(status_code=404, detail="Column not found or access denied")


    db_column.name = column.name
    db_column.position = column.position
    db.commit()
    db.refresh(db_column)
    return db_column


# Delete a column
@router.delete("/{column_id}")
def delete_column(column_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db_column = (
        db.query(ColumnModel)
        .join(Board)
        .join(Project)
        .filter(ColumnModel.id == column_id, Project.owner_id == current_user.user_id)
        .first()
    )
    if not db_column:
        raise HTTPException(status_code=404, detail="Column not found or access denied")

    db.delete(db_column)
    db.commit()
    return {"message": "Column deleted successfully"}
