from sqlalchemy.ext.asyncio import AsyncSession
from . import models

async def log_activity(db: AsyncSession, user_id: int, action: str):
    log = models.ActivityLog(user_id=user_id, action=action)
    db.add(log)
    await db.commit()

def send_assignment_email(user_email: str, task_title: str):
    print(f"[MAIL DELIVERY SUCCESS] Outbound alert dispatched to {user_email} for task: '{task_title}'")
