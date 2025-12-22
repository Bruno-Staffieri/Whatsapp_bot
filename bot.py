import time
import os
from datetime import datetime, timedelta

from twilio.rest import Client
from sqlalchemy.orm import Session

from database import get_session
from models import UserConfig, Recipient


# =========================
# VARIABLES DE ENTORNO
# =========================
ACCOUNT_SID = os.getenv("TWILIO_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
FROM_NUMBER = os.getenv("TWILIO_PHONE")

if not all([ACCOUNT_SID, AUTH_TOKEN, FROM_NUMBER]):
    raise RuntimeError("Faltan variables de entorno de Twilio")

client = Client(ACCOUNT_SID, AUTH_TOKEN)


# =========================
# ENVÍO DE MENSAJE
# =========================
def send_messages():
    session: Session = get_session()

    try:
        cfg = session.query(UserConfig).first()
        recipients = session.query(Recipient).all()

        if not cfg or not recipients:
            return

        for r in recipients:
            try:
                msg = client.messages.create(
                    from_=FROM_NUMBER,
                    to=f"whatsapp:{r.phone}",
                    body=cfg.message
                )
                print(f"Mensaje enviado a {r.phone}. SID: {msg.sid}")
            except Exception as e:
                print(f"Error al enviar mensaje a {r.phone}: {e}")

    finally:
        session.close()


# =========================
# LOOP PRINCIPAL
# =========================
def main_loop():
    print("Scheduler iniciado. Esperando la hora programada...")

    sent_today = False
    last_day = None

    while True:
        # Hora Argentina (UTC - 3)
        now = datetime.utcnow() - timedelta(hours=3)

        session: Session = get_session()
        try:
            cfg = session.query(UserConfig).first()
        finally:
            session.close()

        if not cfg:
            time.sleep(30)
            continue

        # Reset diario
        if last_day != now.date():
            sent_today = False
            last_day = now.date()

        # DEBUG (podés borrar luego)
        # print(f"Hora servidor AR: {now.hour}:{now.minute}")
        # print(f"Hora guardada: {cfg.send_hour}:{cfg.send_minute}")

        if (
            now.hour == cfg.send_hour and
            now.minute == cfg.send_minute and
            not sent_today
        ):
            send_messages()
            sent_today = True

        time.sleep(20)


# =========================
# ENTRY POINT
# =========================
if __name__ == "__main__":
    main_loop()
