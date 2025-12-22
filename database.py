from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, UserConfig, Recipient

DATABASE_URL = "sqlite:///whatsapp_scheduler.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_config():
    session = SessionLocal()
    try:
        config = session.query(UserConfig).first()

        if not config:
            return {
                "message": "",
                "send_hour": 12,
                "send_minute": 0,
                "recipients": []
            }

        recipients = [
            r.phone for r in session.query(Recipient).all()
        ]

        return {
            "message": config.message,
            "send_hour": config.send_hour,
            "send_minute": config.send_minute,
            "recipients": recipients
        }
    finally:
        session.close()


def save_config(message=None, send_hour=None, send_minute=None):
    session = SessionLocal()
    try:
        config = session.query(UserConfig).first()

        if not config:
            config = UserConfig()
            session.add(config)

        if message is not None:
            config.message = message
        if send_hour is not None:
            config.send_hour = send_hour
        if send_minute is not None:
            config.send_minute = send_minute

        session.commit()
    finally:
        session.close()


def save_recipients(phones):
    session = SessionLocal()
    try:
        session.query(Recipient).delete()

        for phone in phones:
            if phone:
                session.add(Recipient(phone=phone))

        session.commit()
    finally:
        session.close()
