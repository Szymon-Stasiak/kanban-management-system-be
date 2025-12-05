from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import get_db
from app.models.task import Task
from app.models.column import ColumnModel
from app.models.board import Board
from app.models.project import Project
from app.schemas.task_schema import TaskCreate, TaskOut, TaskUpdate
from typing import List
from app.services.jwt_service import get_current_user

router = APIRouter()

# Create a column in a board
@router.post("/create", response_model=TaskOut)
def create_task(task: TaskCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):

    # Ensure column belongs to the user
    column = (
        db.query(ColumnModel)
        .join(Board)
        .join(Project)
        .filter(
            ColumnModel.id == task.column_id,
            Project.owner_id == current_user.user_id
        )
        .first()
    )

    if not column:
        raise HTTPException(status_code=404, detail="Column not found or access denied")

    new_task = Task(
        title=task.title,
        description=task.description,
        position=task.position,
        column_id=task.column_id,
        priority=task.priority,
        due_date=task.due_date,
        completed=task.completed,
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task


@router.get("/getall", response_model=List[TaskOut])
def get_all_tasks(db: Session = Depends(get_db), current_user=Depends(get_current_user)):

    tasks = (
        db.query(Task)
        .join(ColumnModel)
        .join(Board)
        .join(Project)
        .filter(Project.owner_id == current_user.user_id)
        .all()
    )

    return tasks


@router.get("/{column_id}", response_model=List[TaskOut])
def get_tasks_for_column(column_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):

    tasks = (
        db.query(Task)
        .join(ColumnModel)
        .join(Board)
        .join(Project)
        .filter(
            Task.column_id == column_id,
            Project.owner_id == current_user.user_id
        )
        .order_by(Task.position)
        .all()
    )

    return tasks


# Update a task
@router.put("/update/{task_id}", response_model=TaskOut)
def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):

    existing = (
        db.query(Task)
        .join(ColumnModel)
        .join(Board)
        .join(Project)
        .filter(
            Task.id == task_id,
            Project.owner_id == current_user.user_id,
        )
        .first()
    )

    if not existing:
        raise HTTPException(status_code=404, detail="Task not found or access denied")

    if task.title is not None:
        existing.title = task.title
    if task.description is not None:
        existing.description = task.description
    # Handle reordering when position (and optionally column_id) provided
    if task.position is not None:
        new_position = task.position
        target_column_id = task.column_id if task.column_id is not None else existing.column_id

        # Determine max position in target column
        max_position = db.query(func.max(Task.position)).filter(Task.column_id == target_column_id).scalar() or 0

        if new_position < 1:
            raise HTTPException(status_code=400, detail="Invalid position")

        # If moving to a different column, clamp new_position to max+1
        if target_column_id != existing.column_id:
            # Removing from old column: shift left positions after the old position
            db.query(Task).filter(Task.column_id == existing.column_id).filter(Task.position > (existing.position or 0)).update({Task.position: Task.position - 1}, synchronize_session=False)

            # Insert into new column: clamp new_position
            if new_position > max_position + 1:
                new_position = max_position + 1

            # Shift tasks at or after new_position in new column to the right
            db.query(Task).filter(Task.column_id == target_column_id).filter(Task.position >= new_position).update({Task.position: Task.position + 1}, synchronize_session=False)

            existing.position = new_position
            existing.column_id = target_column_id
        else:
            # Moving within same column
            old_position = existing.position or 0
            if new_position == old_position:
                pass
            else:
                if new_position > old_position:
                    # shift left tasks between old_position+1 .. new_position
                    db.query(Task).filter(Task.column_id == existing.column_id).filter(Task.position > old_position).filter(Task.position <= new_position).update({Task.position: Task.position - 1}, synchronize_session=False)
                else:
                    # shift right tasks between new_position .. old_position-1
                    db.query(Task).filter(Task.column_id == existing.column_id).filter(Task.position >= new_position).filter(Task.position < old_position).update({Task.position: Task.position + 1}, synchronize_session=False)

                existing.position = new_position

    if task.column_id is not None and task.position is None:
        # If only column_id changed without position, append to end of that column
        target_column_id = task.column_id
        max_position = db.query(func.max(Task.position)).filter(Task.column_id == target_column_id).scalar() or 0
        # Remove from old column positions
        db.query(Task).filter(Task.column_id == existing.column_id).filter(Task.position > (existing.position or 0)).update({Task.position: Task.position - 1}, synchronize_session=False)
        existing.column_id = target_column_id
        existing.position = max_position + 1
    if task.priority is not None:
        existing.priority = task.priority
    if task.completed is not None:
        existing.completed = task.completed
    if task.due_date is not None:
        existing.due_date = task.due_date

    db.commit()
    db.refresh(existing)

    return existing


# Delete a task
@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):

    existing = (
        db.query(Task)
        .join(ColumnModel)
        .join(Board)
        .join(Project)
        .filter(
            Task.id == task_id,
            Project.owner_id == current_user.user_id,
        )
        .first()
    )

    if not existing:
        raise HTTPException(status_code=404, detail="Task not found or access denied")

    db.delete(existing)
    db.commit()

    return {"detail": "Task deleted"}
