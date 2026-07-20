import asyncio
import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..database import get_db
from .. import models, schemas, oauth2

router = APIRouter(prefix="/auth", tags=["Authentication"])

def hash_password_native(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

def verify_password_native(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

@router.post("/signup", response_model=schemas.UserOut)
async def signup(user: schemas.UserSignUp, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).filter(models.User.email == user.email))
    existing = result.scalars().first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    hashed_password = await asyncio.to_thread(hash_password_native, user.password)
    
    new_user = models.User(
        full_name=user.full_name, 
        email=user.email, 
        password=hashed_password, 
        role=str(user.role.value)
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).filter(models.User.email == form_data.username))
    user = result.scalars().first()
    
    if not user or user.is_deleted:
        raise HTTPException(status_code=400, detail="Invalid Credentials")
        
    is_valid = await asyncio.to_thread(verify_password_native, form_data.password, user.password)
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid Credentials")
        
    access_token = oauth2.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer", "role": user.role}

@router.get("/me", response_model=schemas.UserOut)
async def get_me(current_user: models.User = Depends(oauth2.get_current_user)):
    return current_user
