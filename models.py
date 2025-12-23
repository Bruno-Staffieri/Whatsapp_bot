from sqlalchemy import Column, Integer, String
from database import Base


class UserConfig(Base):
    __tablename__ = "user_config"

    id = Column(Integer, primary_key=True)
    send_hour = Column(Integer, default=12)
    send_minute = Column(Integer, default=0)
    message = Column(String, default="Mensaje de prueba")


class Recipient(Base):
    __tablename__ = "recipients"

    id = Column(Integer, primary_key=True)
    phone = Column(String, unique=True)