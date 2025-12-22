import os
import threading
import time
from datetime import datetime

from flask import Flask, render_template, request, jsonify
from twilio.rest import Client

from database import init_db, get_config, save_config, save_recipients

# -------------------------
# Configuración Flask
# -------------------------
app = Flask(__name__)

# -------------------------
# Variables de entorno (Render / .env local)
# -------------------------
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = os.environ.get("TWILIO_WHATSAPP_FROM")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# -------------------------
# Inicializar base de datos
# -------------------------
init_db()

# -------------------------
# RUTAS WEB
# -------------------------
@app.route("/")
def index():
    return render_template("index.html")


# -------------------------
# API: Obtener configuración
# -------------------------
@app.route("/api/get-config", methods=["GET"])
def api_get_config():
    config = get_config()
    if not config:
        return jsonify({"error": "No hay configuración"}), 404

    return jsonify({
        "message": config["message"],
        "send_hour": config["send_hour"],
        "send_minute": config["send_minute"],
        "recipients": config["recipients"]
    })


# -------------------------
# API: Guardar mensaje / horario
# -------------------------
@app.route("/api/set-config", methods=["POST"])
def api_set_config():
    data = request.json or {}

    message = data.get("message")
    send_hour = data.get("send_hour")
    send_minute = data.get("send_minute")

    save_config(
        message=message,
        send_hour=send_hour,
        send_minute=send_minute
    )

    return jsonify({"status": "ok"})


# -------------------------
# API: Guardar destinatarios
# -------------------------
@app.route("/api/set-recipients", methods=["POST"])
def api_set_recipients():
    data = request.json or {}
    recipients = data.get("recipients", [])

    save_recipients(recipients)

    return jsonify({"status": "ok"})


# -------------------------
# Scheduler (loop infinito)
# -------------------------
def scheduler_loop():
    print("Scheduler iniciado. Esperando la hora programada...")

    last_sent_date = None

    while True:
        try:
            config = get_config()
            if not config:
                time.sleep(30)
                continue

            now = datetime.now()
            current_hour = now.hour
            current_minute = now.minute
            today = now.date()

            if (
                current_hour == config["send_hour"]
                and current_minute == config["send_minute"]
                and last_sent_date != today
            ):
                for number in config["recipients"]:
                    try:
                        message = client.messages.create(
                            from_=f"whatsapp:{TWILIO_WHATSAPP_FROM}",
                            to=f"whatsapp:{number}",
                            body=config["message"]
                        )
                        print(f"Mensaje enviado a {number}. SID: {message.sid}")
                    except Exception as e:
                        print(f"Error enviando a {number}: {e}")

                last_sent_date = today

            time.sleep(30)

        except Exception as e:
            print("Error en scheduler:", e)
            time.sleep(30)


# -------------------------
# Lanzar scheduler en segundo plano
# -------------------------
threading.Thread(target=scheduler_loop, daemon=True).start()
print("Bot iniciado en segundo plano")


# -------------------------
# Arranque Flask (Render)
# -------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
