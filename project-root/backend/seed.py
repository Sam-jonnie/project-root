import asyncio
import bcrypt
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import AsyncSessionLocal
from app.models import User, Project, ProjectMember, Task, ActivityLog

def hash_pw(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

async def get_or_create_user(db: AsyncSession, full_name: str, email: str, role: str) -> User:
    result = await db.execute(select(User).filter(User.email == email))
    user = result.scalars().first()
    if not user:
        pw = hash_pw("securepassword")
        user = User(full_name=full_name, email=email, password=pw, role=role)
        db.add(user)
        await db.flush()
        print(f"👤 Account provisioned: {email} ({role})")
    else:
        print(f"🔄 Account already active: {email} ({role})")
    return user

async def main():
    print("Connecting to database to seed default data matrices...")
    
    async with AsyncSessionLocal(expire_on_commit=False) as db:
        admin = await get_or_create_user(db, "Deepakrajan J", "deepak@company.com", "Admin")
        manager = await get_or_create_user(db, "Sarah Connor", "sarah@company.com", "Manager")
        member1 = await get_or_create_user(db, "Alex Mercer", "alex@company.com", "Member")
        member2 = await get_or_create_user(db, "Elena Rostova", "elena@company.com", "Member")
        
        await db.commit()

        proj_result = await db.execute(select(Project).filter(Project.name == "Project Apollo"))
        existing_proj = proj_result.scalars().first()
        
        if not existing_proj:
            p1 = Project(name="Project Apollo", description="Neon Dark-Theme Core Grid Overhaul", created_by=admin.id)
            p2 = Project(name="Project Cyberspace", description="FastAPI High-Utility Engine Audit", created_by=manager.id)
            db.add_all([p1, p2])
            await db.flush()
            print("📂 System project pipelines mounted.")

            m1 = ProjectMember(project_id=p1.id, user_id=member1.id)
            m2 = ProjectMember(project_id=p1.id, user_id=member2.id)
            m3 = ProjectMember(project_id=p2.id, user_id=member1.id)
            db.add_all([m1, m2, m3])

            t1 = Task(title="Build Gradient Flexbox UI", description="Implement cool visual layout blocks", status="In Progress", priority="High", due_date=datetime.utcnow() + timedelta(days=3), assigned_to=member1.id, project_id=p1.id)
            t2 = Task(title="Audit Auth Performance", description="Verify only raw bearer token input rules", status="Completed", priority="Medium", due_date=datetime.utcnow() + timedelta(days=1), assigned_to=member2.id, project_id=p1.id)
            t3 = Task(title="Refactor Asynchronous Drivers", description="Optimize underlying asyncpg pipelines", status="Pending", priority="High", due_date=datetime.utcnow() + timedelta(days=5), assigned_to=member1.id, project_id=p2.id)
            t4 = Task(title="Write Automated Documentation", description="Build complete layout guides", status="Pending", priority="Low", due_date=datetime.utcnow() + timedelta(days=7), assigned_to=admin.id, project_id=p2.id)
            db.add_all([t1, t2, t3, t4])

            log = ActivityLog(user_id=admin.id, action="Initialized default development seed bundle data sets.")
            db.add(log)
            
            await db.commit()
            print("Tasks and activity track records fully seeded!")
        else:
            print("Project structures already initialized. Skipping task seeding.")

        print("\nSYSTEM SEED SCRIPTS SYNCHRONIZED COMPLETED.")

if __name__ == "__main__":
    asyncio.run(main())
