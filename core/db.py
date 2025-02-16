from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy import create_engine
from typing import Annotated
from core.config import DB_PATH

engine = create_engine(DB_PATH, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency Injection for Database Session
SessionDep = Annotated[Session, SessionLocal]
