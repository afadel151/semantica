from sqlmodel import SQLModel, create_engine, Session
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  
DB_PATH = BASE_DIR / "storage" / "database" / "database.db"

DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    echo=True,  # false in prod
    connect_args={"check_same_thread": False}  
)


def init_db():
    """Create all tables defined in SQLModel models."""
    from app import models  #  ensure all models are imported so their metadata is registered
    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependency for FastAPI routes to get a DB session."""
    with Session(engine) as session:
        yield session
