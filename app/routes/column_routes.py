from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.column import ColumnModel
from app.models.board import Board
from app.models.project import Project
from app.schemas.column_schema import ColumnCreate, ColumnOut, ColumnReorder
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

    # Calculate the next position automatically
    max_position = db.query(func.max(ColumnModel.position))\
        .filter(ColumnModel.board_id == column.board_id)\
        .scalar() or 0

    new_column = ColumnModel(
        name=column.name,
        position=max_position + 1, 
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
        .order_by(ColumnModel.position)  
        .all()
    )
    return columns


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

    deleted_position = db_column.position
    board_id = db_column.board_id

    db.delete(db_column)
    
    # Shift columns after the deleted one
    db.query(ColumnModel)\
        .filter(ColumnModel.board_id == board_id)\
        .filter(ColumnModel.position > deleted_position)\
        .update({ColumnModel.position: ColumnModel.position - 1}, synchronize_session=False)
    
    db.commit()
    return {"message": "Column deleted successfully"}


@router.put("/{column_id}/reorder", response_model=ColumnOut)
def reorder_column(
    column_id: int, 
    reorder_data: ColumnReorder, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    # Verify ownership and get column
    db_column = (
        db.query(ColumnModel)
        .join(Board)
        .join(Project)
        .filter(ColumnModel.id == column_id, Project.owner_id == current_user.user_id)
        .first()
    )
    if not db_column:
        raise HTTPException(status_code=404, detail="Column not found or access denied")

    old_position = db_column.position
    new_position = reorder_data.new_position
    board_id = db_column.board_id

    # Validate new position
    max_position = db.query(func.max(ColumnModel.position))\
        .filter(ColumnModel.board_id == board_id)\
        .scalar() or 0
    
    if new_position < 1 or new_position > max_position:
        raise HTTPException(status_code=400, detail="Invalid position")

    if old_position == new_position:
        return db_column

    # Reorder logic
    if old_position < new_position:
        # Moving right: shift columns between old and new position to the left
        db.query(ColumnModel)\
            .filter(ColumnModel.board_id == board_id)\
            .filter(ColumnModel.position > old_position)\
            .filter(ColumnModel.position <= new_position)\
            .update({ColumnModel.position: ColumnModel.position - 1}, synchronize_session=False)
    else:
        # Moving left: shift columns between new and old position to the right
        db.query(ColumnModel)\
            .filter(ColumnModel.board_id == board_id)\
            .filter(ColumnModel.position >= new_position)\
            .filter(ColumnModel.position < old_position)\
            .update({ColumnModel.position: ColumnModel.position + 1}, synchronize_session=False)

    # Update the dragged column position
    db_column.position = new_position
    db.commit()
    db.refresh(db_column)
    
    return db_column
