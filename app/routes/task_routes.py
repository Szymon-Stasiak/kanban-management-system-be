from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
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
        .all()
    )

    return tasks


# Update a task
@router.put("/{task_id}", response_model=TaskOut)
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
    if task.position is not None:
        existing.position = task.position
    if task.column_id is not None:
        existing.column_id = task.column_id
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
