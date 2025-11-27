from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.task import Task
from app.models.column import ColumnModel
from app.models.board import Board
from app.models.project import Project
from app.schemas.task_schema import TaskCreate, TaskOut
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
