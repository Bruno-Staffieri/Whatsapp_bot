import time
from datetime import datetime
from twilio.rest import Client
from dotenv import load_dotenv
import os

from database import get_session
from models import UserConfig, Recipient

# Cargar variables de entorno
load_dotenv()

ACCOUNT_SID = os.getenv("ACCOUNT_SID")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
FROM_NUMBER = os.getenv("FROM_NUMBER")

# Verificación rápida de credenciales
if not ACCOUNT_SID or not AUTH_TOKEN or not FROM_NUMBER:
    raise ValueError("Revisá tu .env: faltan ACCOUNT_SID, AUTH_TOKEN o FROM_NUMBER")

client = Client(ACCOUNT_SID, AUTH_TOKEN)

def send_whatsapp_message(body, to):
    if not to.startswith("whatsapp:"):
        to = f"whatsapp:{to}"  # asegura que Twilio lo reciba como WhatsApp
    try:
        message = client.messages.create(
            from_=FROM_NUMBER,
            body=body,
            to=to
        )
        print(f"Mensaje enviado a {to}. SID: {message.sid}")
    except Exception as e:
        print(f"Error al enviar mensaje a {to}: {e}")

def main_loop():
    print("Scheduler iniciado. Esperando la hora programada...")

    while True:
        now = datetime.now()

        with get_session() as session:
            cfg = session.query(UserConfig).first()
            if cfg is None:
                continue  # Si no hay config, espera

            recipients = [r.phone for r in session.query(Recipient).all()]

        # Si llegó la hora programada, enviar mensaje
        if now.hour == cfg.send_hour and now.minute == cfg.send_minute:
            for phone in recipients:
                send_whatsapp_message(cfg.message, phone)
            # Esperar 60 segundos para no enviar repetidamente el mismo minuto
            time.sleep(60)
        else:
            time.sleep(1)

if __name__ == "__main__":
    main_loop()
