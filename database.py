import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base  # 🔹 Importa Base desde models, no al revés

# 🔹 Ruta de la base de datos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "whatsapp_scheduler.db")

# 🔹 Motor de SQLite
engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine)

def init_db():
    # 🔹 Crea tablas si no existen
    Base.metadata.create_all(bind=engine)

def get_session():
    return SessionLocal()