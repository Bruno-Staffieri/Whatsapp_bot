from sqlalchemy import Column, Integer, String
from database import Base


class UserConfig(Base):
    __tablename__ = "user_config"

    id = Column(Integer, primary_key=True)
    send_hour = Column(Integer, nullable=False)
    send_minute = Column(Integer, nullable=False)
    message = Column(String, nullable=False)


class Recipient(Base):
    __tablename__ = "recipients"

    id = Column(Integer, primary_key=True)
    phone = Column(String, nullable=False)