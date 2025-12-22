from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import threading

from database import init_db, get_session
from models import UserConfig, Recipient
from bot import main_loop

app = Flask(__name__)
CORS(app)

# =========================
# Inicializar base de datos
# =========================
init_db()

# =========================
# FRONTEND
# =========================
@app.route("/")
def home():
    return render_template("index.html")

# =========================
# API – CONFIGURACIÓN
# =========================
@app.route("/api/get-config", methods=["GET"])
def get_config():
    session = get_session()
    cfg = session.query(UserConfig).first()

    if not cfg:
        return jsonify({"error": "config_not_found"}), 404

    recipients = [r.phone for r in session.query(Recipient).all()]

    return jsonify({
        "send_hour": cfg.send_hour,
        "send_minute": cfg.send_minute,
        "message": cfg.message,
        "recipients": recipients
    })


@app.route("/api/set-config", methods=["POST"])
def set_config():
    data = request.json
    session = get_session()

    cfg = session.query(UserConfig).first()
    if not cfg:
        return jsonify({"error": "config_not_found"}), 404

    if "send_hour" in data:
        cfg.send_hour = int(data["send_hour"])

    if "send_minute" in data:
        cfg.send_minute = int(data["send_minute"])

    if "message" in data:
        cfg.message = data["message"]

    session.commit()
    return jsonify({"status": "ok"})


@app.route("/api/set-recipients", methods=["POST"])
def set_recipients():
    data = request.json
    session = get_session()

    session.query(Recipient).delete()

    for phone in data.get("recipients", []):
        session.add(Recipient(phone=phone))

    session.commit()
    return jsonify({"status": "ok"})


# =========================
# BOT EN SEGUNDO PLANO
# =========================
def start_bot():
    thread = threading.Thread(target=main_loop, daemon=True)
    thread.start()
    print("Bot iniciado en segundo plano")


start_bot()

# =========================
# MAIN
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
