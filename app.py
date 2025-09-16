# app.py
import os
import json
from datetime import datetime

import pytz
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

import gspread
from google.oauth2.service_account import Credentials


# =========================
# Configuración general
# =========================
APP_TZ = os.getenv("APP_TZ", "America/Guayaquil")
SHEET_ID = os.getenv("SHEET_ID")  # ID del Google Sheet (entre /d/ y /edit)

# Pestañas / hojas
SHEET_NAME_PEDIDOS = os.getenv("SHEET_NAME_PEDIDOS", "PEDIDOS_TAXI")
SHEET_NAME_TURISMO = os.getenv("SHEET_NAME_TURISMO", "PEDIDOS_TURISMO")

# Telegram (opcional)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")   # Opcional
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")       # Opcional

# Credenciales de Service Account (JSON completo como string)
GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# Warnings mínimos
if not SHEET_ID:
    print("[WARN] SHEET_ID no está configurado")
if not GOOGLE_SERVICE_ACCOUNT_JSON:
    print("[WARN] GOOGLE_SERVICE_ACCOUNT_JSON no está configurado; no se podrá abrir la hoja")


# =========================
# App Flask
# =========================
app = Flask(__name__, template_folder="templates", static_folder="static")
# CORS abierto para poder llamar desde Telegram u otros orígenes
CORS(app, resources={r"/*": {"origins": "*"}})

_gspread_client = None


def get_gspread_client():
    """
    Autoriza el cliente gspread con la service account.
    """
    global _gspread_client
    if _gspread_client:
        return _gspread_client

    if not GOOGLE_SERVICE_ACCOUNT_JSON:
        raise RuntimeError("Falta GOOGLE_SERVICE_ACCOUNT_JSON")

    try:
        info = json.loads(GOOGLE_SERVICE_ACCOUNT_JSON)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"GOOGLE_SERVICE_ACCOUNT_JSON inválido: {e}")

    creds = Credentials.from_service_account_info(info, scopes=SCOPES)
    _gspread_client = gspread.authorize(creds)
    return _gspread_client


def append_row(sheet_name: str, values: list):
    """
    Agrega una fila a la pestaña indicada.
    """
    gc = get_gspread_client()
    sh = gc.open_by_key(SHEET_ID)
    ws = sh.worksheet(sheet_name)
    ws.append_row(values, value_input_option="USER_ENTERED")


def notify_telegram(text: str):
    """
    Notifica opcionalmente por Telegram (no bloquea el flujo si falla).
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": text}, timeout=10)
    except Exception as e:
        print(f"[WARN] No se pudo notificar por Telegram: {e}")


def now_local_strings():
    """
    Retorna (fecha_str, hora_str) en la zona horaria APP_TZ.
    """
    tz = pytz.timezone(APP_TZ)
    now_local = datetime.now(tz)
    return now_local.strftime("%Y-%m-%d"), now_local.strftime("%H:%M:%S")


# =========================
# Rutas básicas
# =========================
@app.get("/ping")
def ping():
    return "pong", 200


@app.get("/")
def root():
    return "GAVVIP backend OK", 200


# =========================
# TAXI (JSON - usado por taxi.html)
# =========================
@app.post("/api/taxi")
def api_taxi():
    """
    Registra pedidos de TAXI en Google Sheets.
    Espera JSON:
    {
      "nombre": "...", "telefono": "...",
      "origen": "...", "destino": "...",
      "vehiculo": "...", "nota": "...",
      "lat": float|str|null, "lng": float|str|null
    }
    """
    try:
        data = request.get_json(silent=True) or {}

        # Requeridos
        nombre = (data.get("nombre") or "").strip()
        telefono = (data.get("telefono") or "").strip()
        origen = (data.get("origen") or "").strip()
        destino = (data.get("destino") or "").strip()
        vehiculo = (data.get("vehiculo") or "").strip()

        # Opcionales
        nota = (data.get("nota") or "").strip()
        lat = data.get("lat")
        lng = data.get("lng")

        faltantes = [k for k, v in {
            "nombre": nombre,
            "telefono": telefono,
            "origen": origen,
            "destino": destino,
            "vehiculo": vehiculo,
        }.items() if not v]
        if faltantes:
            return jsonify({"success": False, "error": f"Campos faltantes: {', '.join(faltantes)}"}), 400

        fecha, hora = now_local_strings()

        # Orden sugerido de columnas en PEDIDOS_TAXI:
        # [FECHA, HORA, NOMBRE, TELEFONO, ORIGEN, DESTINO, VEHICULO, NOTA, LAT, LNG, ESTADO]
        row = [
            fecha, hora, nombre, telefono, origen, destino, vehiculo, nota,
            lat if lat is not None else "",
            lng if lng is not None else "",
            "PENDIENTE",
        ]

        append_row(SHEET_NAME_PEDIDOS, row)

        # Notificación opcional
        notify_telegram(
            "🚖 Nuevo pedido TAXI\n"
            f"Nombre: {nombre}\n"
            f"Tel: {telefono}\n"
            f"Origen: {origen}\n"
            f"Destino: {destino}\n"
            f"Vehículo: {vehiculo}\n"
            f"Nota: {nota}\n"
            f"Lat/Lng: {lat}, {lng}\n"
            f"{fecha} {hora}"
        )

        return jsonify({"success": True}), 200

    except gspread.WorksheetNotFound:
        return jsonify({"success": False, "error": f"Pestaña no encontrada: {SHEET_NAME_PEDIDOS}"}), 500
    except gspread.SpreadsheetNotFound:
        return jsonify({"success": False, "error": "Spreadsheet no encontrado. Revisa SHEET_ID."}), 500
    except Exception as e:
        return jsonify({"success": False, "error": f"Error servidor: {str(e)}"}), 500


# =========================
# TURISMO (HTML clásico - respaldo)
# =========================
@app.post("/solicitar-turismo")
def solicitar_turismo():
    """
    Respaldo HTML clásico (POST de formulario).
    """
    try:
        nombre = (request.form.get("nombre") or "").strip()
        telefono = (request.form.get("telefono") or "").strip()
        origen = (request.form.get("origen") or "").strip()
        destino = (request.form.get("destino") or "").strip()
        fecha_viaje = (request.form.get("fecha") or "").strip()
        nota = (request.form.get("nota") or "").strip()

        faltantes = [k for k, v in {
            "nombre": nombre,
            "telefono": telefono,
            "origen": origen,
            "destino": destino,
            "fecha": fecha_viaje,
        }.items() if not v]
        if faltantes:
            return f"Campos faltantes: {', '.join(faltantes)}", 400

        fecha, hora = now_local_strings()

        # [FECHA, HORA, NOMBRE, TELEFONO, ORIGEN, DESTINO, FECHA_VIAJE, NOTA, ESTADO]
        row = [fecha, hora, nombre, telefono, origen, destino, fecha_viaje, nota, "PENDIENTE"]
        append_row(SHEET_NAME_TURISMO, row)

        notify_telegram(
            "🌍 Nueva solicitud TURISMO\n"
            f"Nombre: {nombre}\n"
            f"Tel: {telefono}\n"
            f"Origen: {origen}\n"
            f"Destino: {destino}\n"
            f"Fecha Viaje: {fecha_viaje}\n"
            f"Nota: {nota}\n"
            f"{fecha} {hora}"
        )

        return """
        <h2>✅ Solicitud de Turismo enviada con éxito</h2>
        <a href="/">Volver a la página principal</a>
        """, 200

    except gspread.WorksheetNotFound:
        return "Pestaña de turismo no encontrada (SHEET_NAME_TURISMO).", 500
    except gspread.SpreadsheetNotFound:
        return "Spreadsheet no encontrado. Revisa SHEET_ID.", 500
    except Exception as e:
        return f"Error al procesar la solicitud: {str(e)}", 500


# =========================
# TURISMO (JSON - usado por turismo.html via fetch)
# =========================
@app.post("/api/turismo")
def api_turismo():
    """
    Registra solicitudes de TURISMO en Google Sheets.
    Espera JSON:
    {
      "nombre": "...", "telefono": "...",
      "origen": "...", "destino": "...",
      "fecha": "YYYY-MM-DD",
      "nota": "... (opcional)"
    }
    """
    try:
        data = request.get_json(silent=True) or {}

        # Requeridos
        nombre = (data.get("nombre") or "").strip()
        telefono = (data.get("telefono") or "").strip()
        origen = (data.get("origen") or "").strip()
        destino = (data.get("destino") or "").strip()
        fecha_viaje = (data.get("fecha") or "").strip()

        # Opcional
        nota = (data.get("nota") or "").strip()

        faltantes = [k for k, v in {
            "nombre": nombre,
            "telefono": telefono,
            "origen": origen,
            "destino": destino,
            "fecha": fecha_viaje,
        }.items() if not v]
        if faltantes:
            return jsonify({"success": False, "error": f"Campos faltantes: {', '.join(faltantes)}"}), 400

        fecha, hora = now_local_strings()

        # [FECHA, HORA, NOMBRE, TELEFONO, ORIGEN, DESTINO, FECHA_VIAJE, NOTA, ESTADO]
        row = [fecha, hora, nombre, telefono, origen, destino, fecha_viaje, nota, "PENDIENTE"]
        append_row(SHEET_NAME_TURISMO, row)

        notify_telegram(
            "🌍 Nueva solicitud TURISMO\n"
            f"Nombre: {nombre}\n"
            f"Tel: {telefono}\n"
            f"Origen: {origen}\n"
            f"Destino: {destino}\n"
            f"Fecha viaje: {fecha_viaje}\n"
            f"Nota: {nota}\n"
            f"{fecha} {hora}"
        )

        return jsonify({"success": True}), 200

    except gspread.WorksheetNotFound:
        return jsonify({"success": False, "error": "Pestaña de turismo no encontrada (SHEET_NAME_TURISMO)."}), 500
    except gspread.SpreadsheetNotFound:
        return jsonify({"success": False, "error": "Spreadsheet no encontrado. Revisa SHEET_ID."}), 500
    except Exception as e:
        return jsonify({"success": False, "error": f"Error servidor: {str(e)}"}), 500


if __name__ == "__main__":
    # Para pruebas locales
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
