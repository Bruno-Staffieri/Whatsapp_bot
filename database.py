import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base  # 🔴 USAR EL BASE DE MODELS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "whatsapp_scheduler.db")

engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={
        "check_same_thread": False,
        "timeout": 30
    }
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_session():
    return SessionLocal()