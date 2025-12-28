from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from uuid import uuid4

app = FastAPI()

#1. Define the Data Model (Schema)
class Task(BaseModel):
    id: Optional[str] = None
    title: str
    description: Optional[str] = "No description"
    is_completed: bool = False

#2. Simulated Database (In-Memory List)
db: List[Task] = []

@app.get("/")
def read_root():
    return {"message": "Welcome to the Task Tracker API"}

#3. Create a Task (POST)
@app.post("/tasks",response_model=Task)
def create_task(task: Task):
    task.id = str(uuid4()) #Generate unique ID
    db.append(task)
    return task

#4. Get ALL Tasks (GET)
@app.get("/tasks",response_model=List[Task])
def get_tasks():
    return db


