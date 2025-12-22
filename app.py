import os
import threading
import time
from datetime import datetime

from flask import Flask, render_template, request, jsonify
from twilio.rest import Client
from sqlalchemy.orm import Session

from database import init_db, get_session
from models import UserConfig, Recipient

# =========================
# VARIABLES DE ENTORNO
# =========================
ACCOUNT_SID = os.environ.get("ACCOUNT_SID")
AUTH_TOKEN = os.environ.get("AUTH_TOKEN")
FROM_NUMBER = os.environ.get("FROM_NUMBER")  # ej: whatsapp:+14155238886

if not all([ACCOUNT_SID, AUTH_TOKEN, FROM_NUMBER]):
    raise RuntimeError("Faltan variables de entorno de Twilio")

client = Client(ACCOUNT_SID, AUTH_TOKEN)

# =========================
# FLASK
# =========================
app = Flask(__name__)

# =========================
# DB
# =========================
init_db()

# =========================
# RUTAS WEB
# =========================
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/get-config", methods=["GET"])
def get_config_api():
    session: Session = get_session()
    try:
        cfg = session.query(UserConfig).first()
        recipients = session.query(Recipient).all()

        if not cfg:
            return jsonify({"error": "No config"}), 404

        return jsonify({
            "message": cfg.message,
            "send_hour": cfg.send_hour,
            "send_minute": cfg.send_minute,
            "recipients": [r.phone for r in recipients]
        })
    finally:
        session.close()


@app.route("/api/set-config", methods=["POST"])
def set_config_api():
    data = request.json or {}

    session: Session = get_session()
    try:
        cfg = session.query(UserConfig).first()
        if not cfg:
            cfg = UserConfig()
            session.add(cfg)

        cfg.message = data.get("message", cfg.message)
        cfg.send_hour = int(data.get("send_hour"))
        cfg.send_minute = int(data.get("send_minute"))

        session.commit()
        return jsonify({"status": "ok"})
    finally:
        session.close()


@app.route("/api/set-recipients", methods=["POST"])
def set_recipients_api():
    data = request.json or {}
    numbers = data.get("recipients", [])

    session: Session = get_session()
    try:
        session.query(Recipient).delete()
        for n in numbers:
            session.add(Recipient(phone=n))
        session.commit()
        return jsonify({"status": "ok"})
    finally:
        session.close()

# =========================
# SCHEDULER
# =========================
def scheduler_loop():
    print("Scheduler iniciado")

    last_sent_date = None

    while True:
        now = datetime.utcnow()  # PythonAnywhere = UTC
        session: Session = get_session()

        try:
            cfg = session.query(UserConfig).first()
            recipients = session.query(Recipient).all()

            if not cfg or not recipients:
                time.sleep(30)
                continue

            if (
                now.hour == cfg.send_hour and
                now.minute == cfg.send_minute and
                last_sent_date != now.date()
            ):
                for r in recipients:
                    try:
                        msg = client.messages.create(
                            from_=FROM_NUMBER,
                            to=f"whatsapp:{r.phone}",
                            body=cfg.message
                        )
                        print(f"Mensaje enviado a {r.phone} | SID {msg.sid}")
                    except Exception as e:
                        print(f"Error enviando a {r.phone}: {e}")

                last_sent_date = now.date()

        finally:
            session.close()

        time.sleep(20)

# =========================
# THREAD BACKGROUND
# =========================
threading.Thread(target=scheduler_loop, daemon=True).start()
print("Bot iniciado en segundo plano")

# =========================
# START
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
