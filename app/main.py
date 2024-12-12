from fastapi import FastAPI
from app.routers import task, user
from app.backend.db import engine, Base
from app.models import Task, User


Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to Taskmanager"}

app.include_router(task.router)
app.include_router(user.router)