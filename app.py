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
SHEET_ID = os.getenv("SHEET_ID")                       # ID del Google Sheet (entre /d/ y /edit)
SHEET_NAME_PEDIDOS = os.getenv("SHEET_NAME_PEDIDOS", "PEDIDOS_TAXI")  # Nombre de pestaña
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")   # Opcional
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")       # Opcional

GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")  # JSON completo como string

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Validaciones mínimas de entorno
if not SHEET_ID:
    print("[WARN] SHEET_ID no está configurado")
if not GOOGLE_SERVICE_ACCOUNT_JSON:
    print("[WARN] GOOGLE_SERVICE_ACCOUNT_JSON no está configurado; no se podrá abrir la hoja")


# =========================
# App Flask
# =========================
app = Flask(__name__, template_folder="templates", static_folder="static")
# CORS abierto para poder llamar desde Telegram Mini App u orígenes externos
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


def append_pedido_row(values):
    """
    Agrega una fila a la pestaña indicada.
    Orden sugerido de columnas en la hoja:
    [FECHA, HORA, NOMBRE, TELEFONO, ORIGEN, DESTINO, VEHICULO, NOTA, LAT, LNG, ESTADO]
    """
    gc = get_gspread_client()
    sh = gc.open_by_key(SHEET_ID)
    ws = sh.worksheet(SHEET_NAME_PEDIDOS)
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


# =========================
# Rutas
# =========================
@app.get("/ping")
def ping():
    return "pong", 200


@app.get("/")
def root():
    return "GAVVIP backend OK", 200


@app.post("/api/taxi")
def api_taxi():
    """
    Endpoint para registrar pedidos de TAXI en Google Sheets.
    Espera JSON:
    {
      "nombre": "...", "telefono": "...",
      "origen": "...", "destino": "...",
      "vehiculo": "...", "nota": "...",
      "lat": (float|str|null), "lng": (float|str|null)
    }
    """
    try:
        data = request.get_json(silent=True) or {}

        # Campos requeridos
        nombre = (data.get("nombre") or "").strip()
        telefono = (data.get("telefono") or "").strip()
        origen = (data.get("origen") or "").strip()
        destino = (data.get("destino") or "").strip()
        vehiculo = (data.get("vehiculo") or "").strip()

        # Opcionales
        nota = (data.get("nota") or "").strip()
        lat = data.get("lat")
        lng = data.get("lng")

        # Validación mínima
        faltantes = [k for k, v in {
            "nombre": nombre,
            "telefono": telefono,
            "origen": origen,
            "destino": destino,
            "vehiculo": vehiculo
        }.items() if not v]

        if faltantes:
            return jsonify({"success": False, "error": f"Campos faltantes: {', '.join(faltantes)}"}), 400

        # Marca de tiempo local
        tz = pytz.timezone(APP_TZ)
        now_local = datetime.now(tz)
        fecha = now_local.strftime("%Y-%m-%d")
        hora = now_local.strftime("%H:%M:%S")

        # Arma fila (ajusta al orden de tu hoja)
        row = [
            fecha, hora, nombre, telefono, origen, destino, vehiculo, nota,
            lat if lat is not None else "",
            lng if lng is not None else "",
            "PENDIENTE"
        ]

        append_pedido_row(row)

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
        return jsonify({"success": False, "error": "Spreadsheet no encontrado. Revisa SHEET_ID"}), 500
    except Exception as e:
        # Error genérico
        return jsonify({"success": False, "error": f"Error servidor: {str(e)}"}), 500


if __name__ == "__main__":
    # Para pruebas locales
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))


@app.post("/solicitar-turismo")
def solicitar_turismo():
    try:
        nombre = (request.form.get("nombre") or "").strip()
        telefono = (request.form.get("telefono") or "").strip()
        origen = (request.form.get("origen") or "").strip()
        destino = (request.form.get("destino") or "").strip()
        fecha_viaje = (request.form.get("fecha") or "").strip()

        # Validación mínima
        faltantes = [k for k, v in {
            "nombre": nombre,
            "telefono": telefono,
            "origen": origen,
            "destino": destino,
            "fecha": fecha_viaje
        }.items() if not v]

        if faltantes:
            return f"Campos faltantes: {', '.join(faltantes)}", 400

        # Timestamp local
        tz = pytz.timezone(APP_TZ)
        now_local = datetime.now(tz)
        fecha = now_local.strftime("%Y-%m-%d")
        hora = now_local.strftime("%H:%M:%S")

        # Arma fila para la hoja de turismo
        row = [
            fecha, hora, nombre, telefono, origen, destino, fecha_viaje, "PENDIENTE"
        ]

        # Guardar en hoja de turismo
        gc = get_gspread_client()
        sh = gc.open_by_key(SHEET_ID)
        ws = sh.worksheet(os.getenv("SHEET_NAME_TURISMO", "PEDIDOS_TURISMO"))
        ws.append_row(row, value_input_option="USER_ENTERED")

        # Notificación opcional a Telegram
        notify_telegram(
            "🌍 Nueva solicitud TURISMO\n"
            f"Nombre: {nombre}\n"
            f"Tel: {telefono}\n"
            f"Origen: {origen}\n"
            f"Destino: {destino}\n"
            f"Fecha Viaje: {fecha_viaje}\n"
            f"{fecha} {hora}"
        )

        # Mensaje de confirmación simple
        return """
        <h2>✅ Solicitud de Turismo enviada con éxito</h2>
        <a href="/">Volver a la página principal</a>
        """, 200

    except Exception as e:
        return f"Error al procesar la solicitud: {str(e)}", 500


<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <title>Turismo Local y Nacional</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no" />
  <meta name="theme-color" content="#121212" />
  <style>
    :root{
      --bg:#121212; --panel:#1d1d1d; --muted:#2a2a2a;
      --text:#ffffff; --sub:#bdbdbd; --brand:#4facfe; --brand-dark:#008cba;
      --ok:#6BFF95; --error:#ff6b6b;
    }
    *{ box-sizing:border-box; }
    html,body{ height:100%; }
    body{
      margin:0; background:linear-gradient(to bottom, #4facfe, #00f2fe);
      color:var(--text); font-family: Arial, sans-serif;
      display:flex; align-items:center; justify-content:center;
    }
    .wrap{
      width:100%; max-width:520px; padding:20px;
    }
    .card{
      background:#fff; color:#333; border-radius:16px; padding:18px;
      box-shadow:0 10px 30px rgba(0,0,0,.25);
    }
    h1{ margin:6px 0 12px; font-size:22px; color:#444; }
    label{ display:block; margin-top:12px; font-size:13px; color:#666; }
    input, textarea, button{
      width:100%; margin-top:6px; padding:12px; font-size:15px;
      border-radius:12px; border:1px solid #ccc; outline:none;
    }
    input:focus, textarea:focus{ border-color: var(--brand); }
    textarea{ resize: vertical; min-height: 80px; }
    .row{ display:grid; grid-template-columns: 1fr 1fr; gap: 10px; }
    .actions{ margin-top:16px; display:grid; gap:10px; }
    button{
      background:var(--brand); color:#fff; border:none; font-weight:800;
      cursor:pointer; transition:filter .15s ease, transform .05s ease;
    }
    button:hover{ filter:brightness(1.03); }
    button:active{ transform: translateY(1px) scale(0.997); }
    button.secondary{ background:#f0f0f0; color:#333; border:1px solid #ddd; }
    .msg{ margin-top:10px; min-height:18px; font-size:14px; }
    .msg.ok{ color: #1a7f37; }
    .msg.err{ color: var(--error); }
    .back{ text-decoration:none; display:inline-block; margin-top:14px; font-size:14px;
           background:#4facfe; color:#fff; padding:10px 16px; border-radius:10px; }
  </style>
</head>
<body
  <!-- Si el backend está en otro dominio, fija aquí el endpoint absoluto -->
  <!-- data-endpoint="https://TU-DOMINIO.onrender.com/api/turismo" -->
  data-endpoint=""
>
  <div class="wrap">
    <div class="card">
      <h1>Solicitud de Turismo</h1>

      <div class="row">
        <div>
          <label for="nombre">Nombre*</label>
          <input id="nombre" placeholder="Tu nombre" autocomplete="name" />
        </div>
        <div>
          <label for="telefono">Teléfono*</label>
          <input id="telefono" placeholder="+593..." inputmode="tel" autocomplete="tel" />
        </div>
      </div>

      <label for="origen">Origen*</label>
      <input id="origen" placeholder="Ciudad o punto de partida" />

      <label for="destino">Destino*</label>
      <input id="destino" placeholder="Ciudad o lugar de destino" />

      <div class="row">
        <div>
          <label for="fecha">Fecha del viaje*</label>
          <input id="fecha" type="date" />
        </div>
        <div>
          <label for="nota">Notas</label>
          <input id="nota" placeholder="Opcional (pax, tour, preferencias…)" />
        </div>
      </div>

      <div class="actions">
        <button id="btnEnviar" type="button">Enviar Solicitud</button>
        <a class="back" href="/">Volver a la Página Principal</a>
      </div>

      <div id="msg" class="msg"></div>
    </div>
  </div>

  <script>
    function getApiEndpoint(){
      const custom = (document.body.getAttribute("data-endpoint") || "").trim();
      return custom || (location.origin + "/api/turismo");
    }
    function setMsg(t, type){
      const el = document.getElementById("msg");
      el.textContent = t || "";
      el.className = "msg" + (type ? " " + type : "");
    }

    async function enviarSolicitud(){
      const btn = document.getElementById("btnEnviar");
      const nombre = document.getElementById("nombre").value.trim();
      const telefono = document.getElementById("telefono").value.trim();
      const origen = document.getElementById("origen").value.trim();
      const destino = document.getElementById("destino").value.trim();
      const fecha = document.getElementById("fecha").value.trim();
      const nota = document.getElementById("nota").value.trim();

      const faltantes = [];
      if(!nombre) faltantes.push("nombre");
      if(!telefono) faltantes.push("teléfono");
      if(!origen) faltantes.push("origen");
      if(!destino) faltantes.push("destino");
      if(!fecha) faltantes.push("fecha del viaje");
      if(faltantes.length){
        setMsg("Completa: " + faltantes.join(", "), "err");
        return;
      }

      const payload = { nombre, telefono, origen, destino, fecha, nota };
      const endpoint = getApiEndpoint();

      setMsg("Enviando solicitud...", "");
      btn.disabled = true;

      try{
        const res = await fetch(endpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        const data = await res.json().catch(()=> ({}));

        if(!res.ok || !data.success){
          const err = (data && data.error) ? data.error : `HTTP ${res.status}`;
          setMsg("Error de envío: " + err, "err");
          btn.disabled = false;
          return;
        }

        setMsg("✅ Solicitud enviada con éxito", "ok");
        // Limpia algunos campos
        document.getElementById("nota").value = "";
      }catch(e){
        setMsg("Error de envío. Revisa tu conexión o el endpoint.", "err");
      }finally{
        btn.disabled = false;
      }
    }

    document.getElementById("btnEnviar").addEventListener("click", enviarSolicitud);
  </script>
</body>
</html>

