from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, projects, tasks, members, users
from .database import engine, Base
from . import models

app = FastAPI(title="Project Management System with High-Utility RBAC Dashboard Interface")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def init_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("startup")
async def startup_event():
    await init_tables()

app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(members.router)
app.include_router(users.router)

@app.get("/")
def health():
    return {"status": "operational", "gradient_theme": "neon-dark-purple-to-blue"}
