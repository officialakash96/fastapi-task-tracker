from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import models
from database import SessionLocal, engine

# --- CONFIG & SECURITY ---
SECRET_KEY = "supersecretkey" # In real life, use .env!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Create Database Tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# --- DATABASE DEPENDENCY ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- PYDANTIC MODELS ---
class UserCreate(BaseModel):
    username: str
    password: str
    recovery_key: str

class PasswordReset(BaseModel):
    username: str
    recovery_key: str
    new_password: str

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    profession: Optional[str] = None
    age: Optional[int] = None

class UserResponse(BaseModel):
    id: int
    username: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    profession: Optional[str] = None
    age: Optional[int] = None

    class Config:
        from_attributes = True # Allows reading data from the database model

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1)

class TaskResponse(BaseModel):
    id: int
    title: str
    is_completed: bool
    owner_id: int 
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# --- HELPER FUNCTIONS ---
def get_password_hash(password):
    # FIX: Truncate password to 72 bytes to satisfy bcrypt's limit
    return pwd_context.hash(password[:72])

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(models.UserModel).filter(models.UserModel.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# --- AUTH ENDPOINTS ---

@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    # 1. Check existing user based on username
    existing_user = db.query(models.UserModel).filter(models.UserModel.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # 2. Hash password and save
    hashed_pw = get_password_hash(user.password)
    new_user = models.UserModel(
        username=user.username, 
        hashed_password=hashed_pw,
        recovery_key=user.recovery_key
        )
    db.add(new_user)
    db.commit()
    return {"message": "User created successfully"}

@app.post("/reset-password")
def reset_password(reset_data: PasswordReset, db: Session = Depends(get_db)):
    user = db.query(models.UserModel).filter(models.UserModel.username == reset_data.username).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # CHECK: Does the secret key match?
    if user.recovery_key != reset_data.recovery_key:
        raise HTTPException(status_code=400, detail="Invalid Recovery Key")
    
    # UPDATE PASSWORD
    user.hashed_password = get_password_hash(reset_data.new_password)
    db.commit()
    
    return {"message": "Password updated successfully"}

@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.UserModel).filter(models.UserModel.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# --- TASK ENDPOINTS (SECURED) ---

@app.get("/tasks", response_model=List[TaskResponse])
def get_tasks(db: Session = Depends(get_db), current_user: models.UserModel = Depends(get_current_user)):
    # KEY FEATURE: Only return tasks where owner_id matches the logged-in user
    return db.query(models.TaskModel).filter(models.TaskModel.owner_id == current_user.id).all()

@app.post("/tasks", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db), current_user: models.UserModel = Depends(get_current_user)):
    # KEY FEATURE: Automatically assign the task to the current user
    db_task = models.TaskModel(title=task.title, owner_id=current_user.id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: models.UserModel = Depends(get_current_user)):
    # KEY FEATURE: Ensure user can only delete THEIR OWN tasks
    task = db.query(models.TaskModel).filter(
        models.TaskModel.id == task_id, 
        models.TaskModel.owner_id == current_user.id
    ).first()
    
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found or not authorized")
    
    db.delete(task)
    db.commit()
    return {"message": "Task deleted"}


# --- USER PROFILE ENDPOINTS ---

@app.put("/users/me", response_model=UserResponse) # Ensure UserInDB includes new fields if used
def update_user_profile(profile: UserProfileUpdate, db: Session = Depends(get_db), current_user: models.UserModel = Depends(get_current_user)):
    if profile.full_name: current_user.full_name = profile.full_name
    if profile.email: current_user.email = profile.email
    if profile.profession: current_user.profession = profile.profession
    if profile.age: current_user.age = profile.age

    db.commit()
    db.refresh(current_user)
    return current_user

@app.delete("/users/me")
def delete_account(db: Session = Depends(get_db), current_user: models.UserModel = Depends(get_current_user)):
    db.delete(current_user) # This will also delete their tasks due to cascade
    db.commit()
    return {"message": "Account deleted successfully"}

app.mount("/", StaticFiles(directory="static", html=True), name="static")