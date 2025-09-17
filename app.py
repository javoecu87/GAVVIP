from flask import Flask, render_template, request, send_from_directory, jsonify
import telegram
import asyncio
import logging
import requests
import os
import json
from datetime import datetime

from flask_cors import CORS
import gspread
from google.oauth2.service_account import Credentials
import pytz

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# -----------------------------
# Configuración (ENV con fallback)
# -----------------------------
BOT_TOKEN_TAXI = os.getenv('BOT_TOKEN_TAXI', '8146583492:AAG5pa4rkbikdBYiNAEr9tuNCSDRp53yv54')
BOT_TOKEN_VIP  = os.getenv('BOT_TOKEN_VIP',  '7557496462:AAG5pa4rkbikdBYiNAEr9tuNCSDRp53yv54')
CHAT_ID        = os.getenv('CHAT_ID',        '5828174289')

SHEET_ID = os.getenv("SHEET_ID")  # requerido para /api/*
GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")  # string JSON completo
SHEET_NAME_PEDIDOS = os.getenv("SHEET_NAME_PEDIDOS", "PEDIDOS_TAXI")
SHEET_NAME_TURISMO = os.getenv("SHEET_NAME_TURISMO", "PEDIDOS_TURISMO")
APP_TZ = os.getenv("APP_TZ", "America/Guayaquil")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# -----------------------------
# Logging
# -----------------------------
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[logging.StreamHandler()]
)

# -----------------------------
# Google Sheets helpers
# -----------------------------
_gspread_client = None

def get_gspread_client():
    global _gspread_client
    if _gspread_client:
        return _gspread_client
    if not GOOGLE_SERVICE_ACCOUNT_JSON:
        raise RuntimeError("Falta GOOGLE_SERVICE_ACCOUNT_JSON")
    info = json.loads(GOOGLE_SERVICE_ACCOUNT_JSON)
    creds = Credentials.from_service_account_info(info, scopes=SCOPES)
    _gspread_client = gspread.authorize(creds)
    return _gspread_client

def append_row(sheet_name, values):
    if not SHEET_ID:
        raise RuntimeError("Falta SHEET_ID")
    gc = get_gspread_client()
    sh = gc.open_by_key(SHEET_ID)
    ws = sh.worksheet(sheet_name)
    ws.append_row(values, value_input_option="USER_ENTERED")

def now_local_strings():
    tz = pytz.timezone(APP_TZ)
    now_local = datetime.now(tz)
    return now_local.strftime("%Y-%m-%d"), now_local.strftime("%H:%M:%S")

# -----------------------------
# Telegram helpers
# -----------------------------
async def enviar_mensaje_async(mensaje, token, chat_id):
    bot = telegram.Bot(token=token)
    try:
        await bot.send_message(chat_id=chat_id, text=mensaje, parse_mode='Markdown')
        app.logger.debug("Mensaje enviado a Telegram con éxito")
    except Exception as e:
        app.logger.error(f"Error al enviar mensaje a Telegram: {e}")

def enviar_mensaje(mensaje, token, chat_id=None):
    asyncio.run(enviar_mensaje_async(mensaje, token, chat_id or CHAT_ID))

# -----------------------------
# Archivos estáticos
# -----------------------------
@app.route('/static/images/<path:filename>')
def serve_images(filename):
    return send_from_directory('static/images', filename)

# -----------------------------
# Vistas existentes
# -----------------------------
@app.route('/socio')
def socio():
    return render_template('socio.html')

@app.route('/registro_usuario')
def registro_usuario():
    return render_template('registro_usuario.html')

@app.route('/registro_socio')
def registro_socio():
    return render_template('registro_socio.html')

@app.route('/registro-socio', methods=['POST'])
def registro_socio_post():
    try:
        nombres = request.form.get('nombres')
        apellidos = request.form.get('apellidos')
        telefono = request.form.get('telefono')
        correo = request.form.get('correo')
        tipo = request.form.get('tipo')
        placa = request.form.get('placa')
        licencia = request.form.get('licencia')
        contrasena = request.form.get('contrasena')

        datos = {
            "nombre": f"{nombres} {apellidos}",
            "telefono": telefono,
            "correo": correo,
            "tipo": tipo,
            "placa": placa,
            "licencia": licencia,
            "contrasena": contrasena
        }

        url_script = "https://script.google.com/macros/s/AKfycbzP_zTWiDokE6_UNLmMxiPZRtHDfLND7riLgdiJH9fPA-VUX3VIlZEe9Ndacu6xr6VZ6Q/exec"
        requests.post(url_script, json=datos, timeout=15)

        return render_template("success.html", mensaje="¡Registro enviado correctamente!")
    except Exception as e:
        app.logger.error(f"Error al registrar socio: {e}")
        return "Ocurrió un error al enviar el registro.", 500

@app.route('/verificar_socio')
def verificar_socio():
    return render_template('verificar_socio.html')

@app.route('/')
def ventana_emergente():
    return render_template('emergente.html')

@app.route('/principal')
def principal():
    return render_template('principal.html')

@app.route('/taxi-service')
def taxi_service():
    return render_template('taxi.html')

@app.route('/turismo-subventana')
def turismo_subventana():
    return render_template('turismo_subventana.html')

@app.route('/turismo-ecuador')
def turismo_ecuador():
    return render_template('turismo-ecuador.html')

@app.route('/ecuador-420')
def ecuador_420():
    return render_template('ecuador-420.html')

@app.route('/fletes-mudanzas')
def fletes_mudanzas():
    return render_template('fletes_mudanzas.html')

@app.route('/alta-gama')
def alta_gama():
    vehiculos = ['SUV', 'Van', 'Sedan']
    return render_template('alta_gama.html', vehiculos=vehiculos)

@app.route('/apoyo-hoteles')
def apoyo_hoteles():
    return render_template('apoyo_hoteles.html')

# -----------------------------
# Formularios existentes (Telegram)
# -----------------------------
@app.route('/solicitar-fletes-mudanzas', methods=['POST'])
def solicitar_fletes_mudanzas():
    try:
        nombre = request.form.get('nombre')
        telefono = request.form.get('telefono')
        origen = request.form.get('origen')
        destino = request.form.get('destino')
        detalles = request.form.get('detalles')

        mensaje = (
            "*Solicitud de Fletes y Mudanzas*\n\n"
            f"👤 Nombre: {nombre}\n"
            f"📞 Teléfono: {telefono}\n"
            f"📍 Origen: {origen}\n"
            f"🎯 Destino: {destino}\n"
            f"📋 Detalles: {detalles}"
        )
        enviar_mensaje(mensaje, BOT_TOKEN_VIP)
        return render_template('success.html', mensaje="¡Gracias! Tu solicitud de Fletes y Mudanzas ha sido enviada.")
    except Exception as e:
        app.logger.error(f"Error en /solicitar-fletes-mudanzas: {e}")
        return "Error al procesar la solicitud de Fletes y Mudanzas.", 500

@app.route('/solicitar-taxi', methods=['POST'])
def solicitar_taxi():
    try:
        nombre = request.form.get('nombre')
        telefono = request.form.get('telefono')
        origen = request.form.get('origen')
        destino = request.form.get('destino')

        mensaje = (
            "*Solicitud de Taxi*\n\n"
            f"👤 Nombre: {nombre}\n"
            f"📞 Teléfono: {telefono}\n"
            f"📍 Origen: {origen}\n"
            f"🎯 Destino: {destino}"
        )
        enviar_mensaje(mensaje, BOT_TOKEN_TAXI)
        return render_template('success.html', mensaje="¡Gracias! Tu solicitud de taxi ha sido enviada.")
    except Exception as e:
        app.logger.error(f"Error en /solicitar-taxi: {e}")
        return "Error al procesar la solicitud de taxi.", 500

@app.route('/conductor')
def conductor():
    return render_template('conductor.html')

@app.route('/solicitar-turismo-ecuador', methods=['POST'])
def solicitar_turismo_ecuador_post():
    try:
        nombre = request.form.get('nombre')
        telefono = request.form.get('telefono')
        origen = request.form.get('origen')
        destino = request.form.get('destino')
        fecha = request.form.get('fecha')

        mensaje = (
            "*Solicitud de Turismo Ecuador*\n\n"
            f"👤 Nombre: {nombre}\n"
            f"📞 Teléfono: {telefono}\n"
            f"📍 Origen: {origen}\n"
            f"🎯 Destino: {destino}\n"
            f"📅 Fecha: {fecha}"
        )
        enviar_mensaje(mensaje, BOT_TOKEN_TAXI)
        return render_template('success.html', mensaje="¡Gracias! Tu solicitud de Turismo Ecuador ha sido enviada.")
    except Exception as e:
        app.logger.error(f"Error en /solicitar-turismo-ecuador: {e}")
        return "Error al procesar la solicitud de Turismo Ecuador.", 500

@app.route('/solicitar-ecuador-420', methods=['POST'])
def solicitar_ecuador_420_post():
    try:
        nombre = request.form.get('nombre')
        telefono = request.form.get('telefono')
        origen = request.form.get('origen')
        destino = request.form.get('destino')
        fecha = request.form.get('fecha')

        mensaje = (
            "*Solicitud de Ecuador 420*\n\n"
            f"👤 Nombre: {nombre}\n"
            f"📞 Teléfono: {telefono}\n"
            f"📍 Origen: {origen}\n"
            f"🎯 Destino: {destino}\n"
            f"📅 Fecha: {fecha}"
        )
        enviar_mensaje(mensaje, BOT_TOKEN_TAXI)
        return render_template('success.html', mensaje="¡Gracias! Tu solicitud de Ecuador 420 ha sido enviada.")
    except Exception as e:
        app.logger.error(f"Error en /solicitar-ecuador-420: {e}")
        return "Error al procesar la solicitud de Ecuador 420.", 500

# -----------------------------
# Salud
# -----------------------------
@app.route('/ping')
def ping():
    return "pong", 200

# -----------------------------
# API JSON (AJAX/fetch)
# -----------------------------
@app.post("/api/taxi")
def api_taxi():
    try:
        data = request.get_json(silent=True) or {}
        nombre   = (data.get("nombre") or "").strip()
        telefono = (data.get("telefono") or "").strip()
        origen   = (data.get("origen") or "").strip()
        destino  = (data.get("destino") or "").strip()
        vehiculo = (data.get("vehiculo") or "").strip()
        nota     = (data.get("nota") or "").strip()
        lat      = data.get("lat")
        lng      = data.get("lng")

        faltantes = [k for k, v in {
            "nombre": nombre, "telefono": telefono, "origen": origen, "destino": destino, "vehiculo": vehiculo
        }.items() if not v]
        if faltantes:
            return jsonify({"success": False, "error": f"Campos faltantes: {', '.join(faltantes)}"}), 400

        fecha, hora = now_local_strings()
        row = [
            fecha, hora, nombre, telefono, origen, destino, vehiculo, nota,
            lat if lat is not None else "", lng if lng is not None else "", "PENDIENTE"
        ]
        append_row(SHEET_NAME_PEDIDOS, row)

        mensaje = (
            "🚖 *Nuevo pedido TAXI*\n"
            f"👤 {nombre}\n"
            f"📞 {telefono}\n"
            f"📍 {origen} → {destino}\n"
            f"🚗 {vehiculo}\n"
            f"📝 {nota}\n"
            f"📍 Lat/Lng: {lat}, {lng}\n"
            f"🕒 {fecha} {hora}"
        )
        enviar_mensaje(mensaje, BOT_TOKEN_TAXI)

        return jsonify({"success": True}), 200
    except gspread.WorksheetNotFound:
        return jsonify({"success": False, "error": f"Pestaña no encontrada: {SHEET_NAME_PEDIDOS}"}), 500
    except gspread.SpreadsheetNotFound:
        return jsonify({"success": False, "error": "Spreadsheet no encontrado. Revisa SHEET_ID."}), 500
    except Exception as e:
        app.logger.exception("Error en /api/taxi")
        return jsonify({"success": False, "error": f"Error servidor: {str(e)}"}), 500

@app.post("/api/turismo")
def api_turismo():
    try:
        data = request.get_json(silent=True) or {}
        nombre   = (data.get("nombre") or "").strip()
        telefono = (data.get("telefono") or "").strip()
        origen   = (data.get("origen") or "").strip()
        destino  = (data.get("destino") or "").strip()
        fecha_v  = (data.get("fecha") or "").strip()
        nota     = (data.get("nota") or "").strip()

        faltantes = [k for k, v in {
            "nombre": nombre, "telefono": telefono, "origen": origen, "destino": destino, "fecha": fecha_v
        }.items() if not v]
        if faltantes:
            return jsonify({"success": False, "error": f"Campos faltantes: {', '.join(faltantes)}"}), 400

        fecha, hora = now_local_strings()
        row = [fecha, hora, nombre, telefono, origen, destino, fecha_v, nota, "PENDIENTE"]
        append_row(SHEET_NAME_TURISMO, row)

        mensaje = (
            "🌍 *Nueva solicitud TURISMO*\n"
            f"👤 {nombre}\n"
            f"📞 {telefono}\n"
            f"📍 {origen} → {destino}\n"
            f"📅 {fecha_v}\n"
            f"📝 {nota}\n"
            f"🕒 {fecha} {hora}"
        )
        enviar_mensaje(mensaje, BOT_TOKEN_TAXI)

        return jsonify({"success": True}), 200
    except gspread.WorksheetNotFound:
        return jsonify({"success": False, "error": f"Pestaña no encontrada: {SHEET_NAME_TURISMO}"}), 500
    except gspread.SpreadsheetNotFound:
        return jsonify({"success": False, "error": "Spreadsheet no encontrado. Revisa SHEET_ID."}), 500
    except Exception as e:
        app.logger.exception("Error en /api/turismo")
        return jsonify({"success": False, "error": f"Error servidor: {str(e)}"}), 500

# -----------------------------
# Run
# -----------------------------
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
