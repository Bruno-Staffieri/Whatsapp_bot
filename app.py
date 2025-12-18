from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from database import init_db, get_session
from models import UserConfig, Recipient

app = Flask(__name__)
CORS(app)  # Permite que el panel web (HTML/JS) acceda a esta API

# Inicializar base de datos (solo una vez)
init_db()

@app.route("/")
def home():
    return render_template("index.html")

# Obtener configuración
@app.route("/api/get-config", methods=["GET"])
def get_config():
    session = get_session()
    cfg = session.query(UserConfig).first()

    if cfg is None:
        # Crear configuración por defecto si no existe
        cfg = UserConfig(send_hour=12, send_minute=0, message="Mensaje de prueba")
        session.add(cfg)
        session.commit()

    recipients = [r.phone for r in session.query(Recipient).all()]

    return jsonify({
        "send_hour": cfg.send_hour,
        "send_minute": cfg.send_minute,
        "message": cfg.message,
        "recipients": recipients
    })

# Guardar mensaje y horario
@app.route("/api/set-config", methods=["POST"])
def set_config():
    data = request.json
    session = get_session()

    cfg = session.query(UserConfig).first()
    if cfg is None:
        cfg = UserConfig(send_hour=12, send_minute=0, message="Mensaje de prueba")
        session.add(cfg)
        session.commit()

    if "send_hour" in data:
        cfg.send_hour = int(data["send_hour"])
    if "send_minute" in data:
        cfg.send_minute = int(data["send_minute"])
    if "message" in data:
        cfg.message = data["message"]

    session.commit()
    return jsonify({"status": "ok"})

# Guardar destinatarios
@app.route("/api/set-recipients", methods=["POST"])
def set_recipients():
    data = request.json
    session = get_session()

    # Limpiar todos los destinatarios anteriores
    session.query(Recipient).delete()

    # Agregar nuevos
    for phone in data.get("recipients", []):
        session.add(Recipient(phone=phone))

    session.commit()
    return jsonify({"status": "ok"})

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
