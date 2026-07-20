from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from ..database import get_db
from .. import models, schemas, oauth2, services

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.post("", response_model=schemas.ProjectOut)
async def create_project(
    project: schemas.ProjectCreate, 
    db: AsyncSession = Depends(get_db), 
    current_user: models.User = Depends(oauth2.RoleChecker(["Admin", "Manager"]))
):
    new_project = models.Project(
        name=project.name, 
        description=project.description, 
        created_by=current_user.id
    )
    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)
    
    await services.log_activity(db, current_user.id, f"Created Project: {new_project.name}")
    return new_project

@router.get("", response_model=List[schemas.ProjectOut])
async def get_projects(
    skip: int = 0, 
    limit: int = 10, 
    db: AsyncSession = Depends(get_db), 
    current_user: models.User = Depends(oauth2.get_current_user)
):
    if current_user.role == "Admin":
        stmt = select(models.Project).filter(models.Project.is_deleted == False).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()
    
    stmt = (
        select(models.Project)
        .join(models.ProjectMember, models.Project.id == models.ProjectMember.project_id, isouter=True)
        .filter(
            (models.Project.created_by == current_user.id) | (models.ProjectMember.user_id == current_user.id), 
            models.Project.is_deleted == False
        )
        .distinct()
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/{id}", response_model=schemas.ProjectOut)
async def get_project(
    id: int, 
    db: AsyncSession = Depends(get_db), 
    current_user: models.User = Depends(oauth2.get_current_user)
):
    stmt = select(models.Project).filter(models.Project.id == id, models.Project.is_deleted == False)
    result = await db.execute(stmt)
    proj = result.scalars().first()
    
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    return proj

@router.delete("/{id}")
async def delete_project(
    id: int, 
    db: AsyncSession = Depends(get_db), 
    current_user: models.User = Depends(oauth2.RoleChecker(["Admin"]))
):
    stmt = select(models.Project).filter(models.Project.id == id)
    result = await db.execute(stmt)
    proj = result.scalars().first()
    
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
        
    proj.is_deleted = True
    await db.commit()
    await services.log_activity(db, current_user.id, f"Soft-deleted Project ID: {id}")
    return {"detail": "Project marked soft-delete successfully."}
