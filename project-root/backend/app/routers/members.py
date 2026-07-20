from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from ..database import get_db
from .. import models, schemas, oauth2

router = APIRouter(prefix="/projects/{id}/members", tags=["Project Members"])

@router.post("")
async def add_project_member(id: int, user_id: int, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(oauth2.RoleChecker(["Admin", "Manager"]))):
    result = await db.execute(select(models.ProjectMember).filter(models.ProjectMember.project_id == id, models.ProjectMember.user_id == user_id))
    exists = result.scalars().first()
    if exists:
        return {"detail": "User already explicitly attached as a core team member."}
    assoc = models.ProjectMember(project_id=id, user_id=user_id)
    db.add(assoc)
    await db.commit()
    return {"detail": "Member appended successfully."}
