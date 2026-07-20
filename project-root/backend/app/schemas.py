from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from datetime import datetime, timezone
from typing import Optional, List
from .models import RoleEnum, StatusEnum, PriorityEnum

class UserSignUp(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: RoleEnum

class UserOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: RoleEnum
    
    model_config = ConfigDict(from_attributes=True)

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_by: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: StatusEnum = StatusEnum.PENDING
    priority: PriorityEnum = PriorityEnum.LOW
    due_date: Optional[datetime] = None
    assigned_to: Optional[int] = None
    project_id: int

    @field_validator("due_date")
    @classmethod
    def strip_due_date_tz(cls, v):
        if v is not None and v.tzinfo is not None:
            return v.astimezone(timezone.utc).replace(tzinfo=None)
        return v

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[StatusEnum] = None
    priority: Optional[PriorityEnum] = None
    due_date: Optional[datetime] = None
    assigned_to: Optional[int] = None

    @field_validator("due_date")
    @classmethod
    def strip_due_date_tz(cls, v):
        if v is not None and v.tzinfo is not None:
            return v.astimezone(timezone.utc).replace(tzinfo=None)
        return v

class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: StatusEnum
    priority: PriorityEnum
    due_date: Optional[datetime] = None
    assigned_to: Optional[int] = None
    project_id: int
    model_config = ConfigDict(from_attributes=True)

class CommentCreate(BaseModel):
    comment: str

class CommentOut(BaseModel):
    id: int
    task_id: int
    user_id: int
    comment: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
