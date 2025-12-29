from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    recovery_key = Column(String)  # The secret "backup password"
    
    # New Profile Fields
    full_name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    profession = Column(String, nullable=True)
    age = Column(Integer, nullable=True)

    tasks = relationship("TaskModel", back_populates="owner", cascade="all, delete-orphan")

class TaskModel(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, default="No description")
    is_completed = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("UserModel", back_populates="tasks")