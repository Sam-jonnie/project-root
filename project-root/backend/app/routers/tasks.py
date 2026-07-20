from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
import os
from ..database import get_db
from .. import models, schemas, oauth2, services

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("", response_model=schemas.TaskOut)
async def create_task(task: schemas.TaskCreate, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(oauth2.RoleChecker(["Admin", "Manager"]))):
    new_task = models.Task(**task.model_dump())
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    
    if new_task.assigned_to:
        result = await db.execute(select(models.User).filter(models.User.id == new_task.assigned_to))
        assignee = result.scalars().first()
        if assignee:
            background_tasks.add_task(services.send_assignment_email, assignee.email, new_task.title)
            
    await services.log_activity(db, current_user.id, f"Created Task: {new_task.title}")
    return new_task

@router.get("", response_model=List[schemas.TaskOut])
async def get_tasks(status: models.StatusEnum = None, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    stmt = select(models.Task).filter(models.Task.is_deleted == False)
    if current_user.role == "Member":
        stmt = stmt.filter(models.Task.assigned_to == current_user.id)
    if status:
        stmt = stmt.filter(models.Task.status == status)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.put("/{id}", response_model=schemas.TaskOut)
async def update_task(id: int, updated: schemas.TaskUpdate, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    result = await db.execute(select(models.Task).filter(models.Task.id == id, models.Task.is_deleted == False))
    task = result.scalars().first()
    if not task: 
        raise HTTPException(status_code=404, detail="Task unlocated")
    
    if current_user.role == "Member":
        if updated.title or updated.description or updated.assigned_to or updated.due_date:
            raise HTTPException(status_code=403, detail="Members can only update status values")
        if updated.status:
            task.status = updated.status
    else:
        for key, val in updated.model_dump(exclude_unset=True).items():
            setattr(task, key, val)
            
    await db.commit()
    await services.log_activity(db, current_user.id, f"Mutated Task ID target: {id}")
    return task

@router.post("/{id}/comments", response_model=schemas.CommentOut)
async def add_comment(id: int, comment_data: schemas.CommentCreate, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    new_comment = models.TaskComment(task_id=id, user_id=current_user.id, comment=comment_data.comment)
    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)
    return new_comment

@router.get("/{id}/comments", response_model=List[schemas.CommentOut])
async def get_comments(id: int, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    result = await db.execute(select(models.TaskComment).filter(models.TaskComment.task_id == id).order_by(models.TaskComment.created_at.asc()))
    return result.scalars().all()
