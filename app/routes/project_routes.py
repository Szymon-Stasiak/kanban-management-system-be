
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.project import Project
from app.schemas.project_schema import ProjectCreate, ProjectOut, ProjectUpdate
from app.services.jwt_service import get_current_user

router = APIRouter()


@router.post("/add", response_model=ProjectOut)
def create_project(
	project: ProjectCreate,
	current_user = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	new_project = Project(
		name=project.name,
		description=project.description,
		color=project.color,
		archived=project.archived or False,
	)
	db.add(new_project)
	db.commit()
	db.refresh(new_project)
	return new_project


@router.get("/getall", response_model=List[ProjectOut])
def get_projects(db: Session = Depends(get_db)
				  #,current_user = Depends(get_current_user)
				  ):
	projects = db.query(Project).all()
	return projects


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
	project = db.query(Project).filter(Project.project_id == project_id).first()
	if not project:
		raise HTTPException(status_code=404, detail="Project not found")
	return project


@router.put("/update/{project_id}", response_model=ProjectOut)
def update_project(
	project_id: str,
	project_update: ProjectUpdate,
	db: Session = Depends(get_db),
	current_user = Depends(get_current_user),
):
	project = db.query(Project).filter(Project.project_id == project_id).first()
	if not project:
		raise HTTPException(status_code=404, detail="Project not found")

	if project_update.name is not None:
		project.name = project_update.name
	if project_update.description is not None:
		project.description = project_update.description
	if project_update.color is not None:
		project.color = project_update.color
	if project_update.archived is not None:
		project.archived = project_update.archived

	db.commit()
	db.refresh(project)
	return project


@router.delete("/delete/{project_id}")
def delete_project(project_id: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
	project = db.query(Project).filter(Project.project_id == project_id).first()
	if not project:
		raise HTTPException(status_code=404, detail="Project not found")

	# return the deleted project data
	project_data = {
		"project_id": project.project_id,
		"name": project.name,
		"description": project.description,
		"color": project.color,
		"archived": project.archived,
		"created_at": project.created_at,
		"updated_at": project.updated_at,
	}

	db.delete(project)
	db.commit()

	return {"detail": "Project deleted", "project": project_data}
