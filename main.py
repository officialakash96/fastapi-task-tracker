from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles # 1. Import this at the top
from pydantic import BaseModel
from typing import List, Optional
from uuid import uuid4
from pydantic import BaseModel, Field

# 2. Define the 'app' variable BEFORE using it
app = FastAPI()

# --- DATA MODELS ---
class Task(BaseModel):
    id: Optional[str] = None
    title: str = Field(..., min_length=1)
    description: Optional[str] = "No description"
    is_completed: bool = False

# Simulated Database
db: List[Task] = []

# --- API ENDPOINTS ---

# NOTE: We removed the old @app.get("/") "Hello World" endpoint
# because it would conflict with our new website at the same URL.

@app.get("/tasks", response_model=List[Task])
async def get_tasks():
    return db

@app.post("/tasks", response_model=Task)
async def create_task(task: Task):
    task.id = str(uuid4())
    db.append(task)
    return task

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    for index, task in enumerate(db):
        if task.id == task_id:
            db.pop(index)
            return {"message": "Task deleted successfully"}
    raise HTTPException(status_code=404, detail="Task not found")

# --- STATIC FILES (THE WEBSITE) ---
# 3. This MUST be at the very bottom or after 'app' is defined.
# The 'directory="static"' part MUST match your actual folder name.
app.mount("/", StaticFiles(directory="static", html=True), name="static")