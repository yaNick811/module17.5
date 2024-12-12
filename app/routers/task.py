from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated
from sqlalchemy import select, insert, update, delete
from slugify import slugify


from app.backend.db_depends import get_db
from app.models import Task, User
from app.schemas import CreateTask, UpdateTask

router = APIRouter(
    prefix="/task",
    tags=["task"]
)


DBSession = Annotated[Session, Depends(get_db)]

@router.get("/", status_code=status.HTTP_200_OK)
def all_tasks(db: DBSession):
    """Возвращает список всех задач."""
    query = select(Task)
    tasks = db.scalars(query).all()
    return tasks

@router.get("/{task_id}", status_code=status.HTTP_200_OK)
def task_by_id(task_id: int, db: DBSession):
    """Возвращает задачу по её ID."""
    query = select(Task).where(Task.id == task_id)
    task = db.scalar(query)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task was not found")
    return task

@router.post("/create", status_code=status.HTTP_201_CREATED)
def create_task(task: CreateTask, user_id: int, db: DBSession):
    """Создает новую задачу и связывает её с пользователем."""
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found")


    slug = slugify(task.title)


    new_task = Task(
        title=task.title,
        content=task.content,
        priority=task.priority,
        user_id=user_id,
        slug=slug
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return {"status_code": status.HTTP_201_CREATED, "transaction": "Successful"}

@router.put("/update/{task_id}", status_code=status.HTTP_200_OK)
def update_task(task_id: int, task: UpdateTask, db: DBSession):
    """Обновляет данные задачи."""
    query = select(Task).where(Task.id == task_id)
    existing_task = db.scalar(query)

    if existing_task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task was not found")


    existing_task.title = task.title
    existing_task.content = task.content
    existing_task.priority = task.priority

    db.commit()

    return {"status_code": status.HTTP_200_OK, "transaction": "Task update is successful!"}

@router.delete("/delete/{task_id}", status_code=status.HTTP_200_OK)
def delete_task(task_id: int, db: DBSession):
    """Удаляет задачу по её ID."""
    query = select(Task).where(Task.id == task_id)
    existing_task = db.scalar(query)

    if existing_task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task was not found")

    db.delete(existing_task)
    db.commit()

    return {"status_code": status.HTTP_200_OK, "transaction": "Task deleted successfully"}