from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Create the Database URL
# This tells the app to create a file named 'tasks.db' in the current folder
SQLALCHEMY_DATABASE_URL = "sqlite:///./tasks.db"

# 2. Create the Engine
# 'check_same_thread': False is needed only for SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. Create a Session Factory
# This is what we will use to actually talk to the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Base Class for Models
# We will inherit from this class to create our database tables
Base = declarative_base()