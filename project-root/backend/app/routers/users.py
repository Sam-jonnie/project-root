from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from ..database import get_db
from .. import models, schemas, oauth2

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=List[schemas.UserOut])
async def get_users(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(oauth2.RoleChecker(["Admin", "Manager"]))
):
    stmt = select(models.User).filter(models.User.is_deleted == False)
    result = await db.execute(stmt)
    return result.scalars().all()
