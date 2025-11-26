from flask import Flask, render_template, request, send_from_directory, jsonify

import telegram
import asyncio
import logging
import gspread


app = Flask(__name__)

# Tokens de los bots para los formularios
BOT_TOKEN_TAXI = '8146583492:AAFP-9CTNvmNR13aFxvJB6Q1WS0eBbZhAc0'
BOT_TOKEN_VIP = '7557496462:AAG5pa4rkbikdBYiNAEr9tuNCSDRp53yv54'
BOT_TOKEN_TURISMO = '8590651604:AAFXhSpGmtjNy89FBQGQ3xvXVB0t5cakZ8g'

CHAT_ID = '5828174289'  # Reemplaza con el chat ID correcto


# -----------------------------
# Bandeja de solicitudes TAXI
# -----------------------------
SOLICITUDES = []     # Aquí guardamos las solicitudes en memoria (versión 1.0)
NEXT_ID = 1          # Contador simple de IDs


def crear_solicitud(data):
    """
    Crea una solicitud con la estructura estándar:
    id, tipo_servicio, origen, destino, distancia_km, precio, estado, socio_asignado, timestamp
    """
    global NEXT_ID

    solicitud = {
        "id": NEXT_ID,
        "tipo_servicio": data.get("tipo_servicio"),
        "origen": data.get("origen"),
        "destino": data.get("destino"),
        "distancia_km": data.get("distancia_km"),
        "precio": data.get("precio"),
        "estado": "pendiente",
        "socio_asignado": None,
        "timestamp": data.get("timestamp"),
    }

    SOLICITUDES.append(solicitud)
    NEXT_ID += 1
    return solicitud


# Configuración de logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[logging.StreamHandler()]
)


# ================== GOOGLE SHEETS ==================
import gspread

GC_CREDS_PATH = "/etc/gavvip-credenciales.json"
gc = gspread.service_account(filename=GC_CREDS_PATH)

# Hoja donde se guardan TODOS los pedidos generados por los usuarios
sh_pedidos = gc.open('pedidos')
ws_pedidos = sh_pedidos.sheet1     # o .worksheet('PEDIDOS') si le pusiste nombre

# Hoja donde se guardan los pedidos ya aceptados / terminados
sh_pedidos_completados = gc.open('pedidos completados')
ws_pedidos_completados = sh_pedidos_completados.sheet1   # o .worksheet('PEDIDOS COMPLETADOS')



def to_float_or_none(valor):
    try:
        if not valor:
            return None
        return float(str(valor).replace(',', '.'))
    except Exception:
        return None



# Función asincrónica para enviar el mensaje a Telegram
async def enviar_mensaje_async(mensaje, token):
    bot = telegram.Bot(token=token)
    try:
        await bot.send_message(chat_id=CHAT_ID, text=mensaje, parse_mode='Markdown')
        app.logger.debug("Mensaje enviado a Telegram con éxito")
    except Exception as e:
        app.logger.error(f"Error al enviar mensaje a Telegram: {e}")

# Función para ejecutar el envío de manera asincrónica en cada solicitud
def enviar_mensaje(mensaje, token):
    asyncio.run(enviar_mensaje_async(mensaje, token))

# ✅ Nueva función para servir archivos en static/images/
@app.route('/static/images/<path:filename>')
def serve_images(filename):
    return send_from_directory('static/images', filename)

@app.route('/socio')
def socio():
    return render_template('socio.html')


@app.route('/registro_socio')
def registro_socio():
    return render_template('registro_socio.html')


@app.route('/verificar_socio')
def verificar_socio():
    return render_template('verificar_socio.html')



# Rutas de la ventana principal y sus botones
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

@app.route('/turismo')
def turismo():
    return render_template('turismo.html')


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

@app.route('/alta-gama/formulario')
def formulario_alta_gama():
    # Tomamos el vehículo desde la URL ?vehiculo=SUV
    vehiculo = request.args.get('vehiculo', 'No especificado')
    return render_template('formulario_alta_gama.html', vehiculo=vehiculo)


@app.route('/apoyo-hoteles')
def apoyo_hoteles():
    return render_template('apoyo_hoteles.html')

# Procesar formulario de Fletes y Mudanzas
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

        # Enviar mensaje a Telegram
        enviar_mensaje(mensaje, BOT_TOKEN_VIP)

        return render_template('success.html', mensaje="¡Gracias! Tu solicitud de Fletes y Mudanzas ha sido enviada.")
    except Exception as e:
        app.logger.error(f"Error en /solicitar-fletes-mudanzas: {e}")
        return "Error al procesar la solicitud de Fletes y Mudanzas.", 500

@app.route('/solicitar-turismo', methods=['POST'])
def solicitar_turismo():
    try:
        nombre = request.form.get('nombre')
        telefono = request.form.get('telefono')
        origen = request.form.get('origen')
        destino = request.form.get('destino')
        fecha = request.form.get('fecha')

        mensaje = (
            "*Solicitud de Turismo Local y Nacional*\n\n"
            f"👤 Nombre: {nombre}\n"
            f"📞 Teléfono: {telefono}\n"
            f"📍 Origen: {origen}\n"
            f"🎯 Destino: {destino}\n"
            f"📅 Fecha: {fecha}"
        )

        # Enviar mensaje usando el nuevo bot de Turismo
        enviar_mensaje(mensaje, BOT_TOKEN_TURISMO)

        return render_template(
            'success.html',
            mensaje="¡Gracias! Tu solicitud de Turismo ha sido enviada."
        )
    except Exception as e:
        app.logger.error(f"Error en /solicitar-turismo: {e}")
        return "Error al procesar la solicitud de Turismo.", 500


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

        enviar_mensaje(mensaje, BOT_TOKEN_TAXI,)
        return render_template('success.html', mensaje="¡Gracias! Tu solicitud de taxi ha sido enviada.")
    except Exception as e:
        app.logger.error(f"Error en /solicitar-taxi: {e}")
        return "Error al procesar la solicitud de taxi.", 500

@app.route('/conductor')
def conductor():
    return render_template('conductor.html')


@app.route('/solicitar-turismo-ecuador', methods=['POST'])
def solicitar_turismo_ecuador():
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

        enviar_mensaje(mensaje, BOT_TOKEN_TAXI,)
        return render_template('success.html', mensaje="¡Gracias! Tu solicitud de Turismo Ecuador ha sido enviada.")
    except Exception as e:
        app.logger.error(f"Error en /solicitar-turismo-ecuador: {e}")
        return "Error al procesar la solicitud de Turismo Ecuador.", 500

@app.route('/solicitar-ecuador-420', methods=['POST'])
def solicitar_ecuador_420():
    try:
        nombre = request.form.get('nombre')
        telefono = request.form.get('telefono')
        ciudad = request.form.get('ciudad')
        fecha = request.form.get('fecha')
        detalles = request.form.get('detalles')

        mensaje = (
            "*Solicitud Ecuador 420*\n\n"
            f"👤 Nombre: {nombre}\n"
            f"📞 Teléfono: {telefono}\n"
            f"📍 Ciudad / Provincia: {ciudad}\n"
            f"📅 Fecha tentativa: {fecha}\n"
            f"📋 Detalles: {detalles}"
        )

        # Mismo bot que Turismo
        enviar_mensaje(mensaje, BOT_TOKEN_TURISMO)

        return render_template(
            'success.html',
            mensaje="¡Gracias! Tu solicitud Ecuador 420 ha sido enviada."
        )
    except Exception as e:
        app.logger.error(f"Error en /solicitar-ecuador-420: {e}")
        return "Error al procesar la solicitud Ecuador 420.", 500


@app.route('/procesar_solicitud_alta_gama', methods=['POST'])
def procesar_solicitud_alta_gama():
    try:
        nombre = request.form.get('nombre')
        telefono = request.form.get('telefono')
        vehiculo = request.form.get('tipo_vehiculo')
        fecha = request.form.get('fecha')
        hora = request.form.get('hora')
        detalles = request.form.get('detalles')

        mensaje = (
            "*Solicitud de Alta Gama*\n\n"
            f"👤 Nombre: {nombre}\n"
            f"📞 Teléfono: {telefono}\n"
            f"🚗 Vehículo: {vehiculo}\n"
            f"📅 Fecha: {fecha}\n"
            f"⏰ Hora: {hora}\n"
            f"📋 Detalles: {detalles}"
        )

        # Usamos el bot VIP para este servicio
        enviar_mensaje(mensaje, BOT_TOKEN_VIP)

        return render_template(
            'success.html',
            mensaje="¡Gracias! Tu solicitud de Alta Gama ha sido enviada."
        )
    except Exception as e:
        app.logger.error(f"Error en /procesar_solicitud_alta_gama: {e}")
        return "Error al procesar la solicitud de Alta Gama.", 500


# ===================== API PARA SOLICITUDES DEL BOTÓN TAXI =====================

@app.route('/api/solicitudes', methods=['POST'])
def api_crear_solicitud():
    """
    Recibe una solicitud desde taxi.html en formato JSON
    y la guarda en memoria.
    """
    from datetime import datetime
    global NEXT_ID, SOLICITUDES

    data = request.get_json(silent=True) or {}

    tipo_servicio = data.get('tipo_servicio')
    origen = data.get('origen')
    destino = data.get('destino')
    distancia_km = data.get('distancia_km')
    precio = data.get('precio')
    timestamp = data.get('timestamp') or datetime.utcnow().isoformat()

    if not tipo_servicio or not destino:
        return jsonify({
            "ok": False,
            "error": "Faltan datos obligatorios (tipo_servicio o destino)."
        }), 400

    solicitud = {
        "id": NEXT_ID,
        "tipo_servicio": tipo_servicio,
        "origen": origen,
        "destino": destino,
        "distancia_km": distancia_km,
        "precio": precio,
        "timestamp": timestamp,
        "estado": "pendiente"
    }
    NEXT_ID += 1
    SOLICITUDES.append(solicitud)


    # Guardar también en la hoja "pedidos"
    try:
        # Puedes ajustar el orden/columnas como tú quieras
        fila_pedidos = [
            solicitud["id"],           # ID
            solicitud["tipo_servicio"],
            solicitud["origen"],
            solicitud["destino"],
            solicitud["distancia_km"],
            solicitud["precio"],
            solicitud["timestamp"],
            solicitud["estado"],
        ]
        ws_pedidos.append_row(fila_pedidos)
    except Exception as e:
        app.logger.error(f"Error guardando pedido en hoja 'pedidos': {e}")



    # Opcional: avisar por Telegram mientras no hay lógica de socio.html
    try:
        mensaje = (
            "*Nueva solicitud desde botón TAXI*\n\n"
            f"🚖 Servicio: {tipo_servicio}\n"
            f"📍 Origen: {origen or 'No especificado'}\n"
            f"🎯 Destino: {destino}\n"
        )
        enviar_mensaje(mensaje, BOT_TOKEN_TAXI)
    except Exception as e:
        app.logger.error(f"Error enviando aviso de solicitud a Telegram: {e}")

    return jsonify({"ok": True, "solicitud": solicitud}), 200



@app.route('/api/solicitudes', methods=['GET'])
def api_listar_solicitudes():
    """
    Devuelve solo las solicitudes PENDIENTES.
    socio.html consulta aquí.
    """
    pendientes = [s for s in SOLICITUDES if s.get("estado") == "pendiente"]
    return jsonify({
        "ok": True,
        "solicitudes": pendientes
    }), 200



@app.route('/api/solicitudes/<int:solicitud_id>/aceptar', methods=['POST'])
def api_aceptar_solicitud(solicitud_id):
    """
    Acepta una solicitud:
    - La busca en SOLICITUDES (memoria)
    - Cambia su estado a 'aceptada'
    - La registra en la hoja 'pedidos completados'
    - Devuelve la info para que socio.html muestre 'Viaje en curso'
    """
    try:
        # 1) Buscar la solicitud en la lista SOLICITUDES
        solicitud_encontrada = None
        for s in SOLICITUDES:
            if s["id"] == solicitud_id:
                solicitud_encontrada = s
                break

        if not solicitud_encontrada:
            return jsonify({
                "ok": False,
                "error": f"Solicitud con ID {solicitud_id} no encontrada"
            }), 404

        # 2) Marcar como aceptada en memoria
        solicitud_encontrada["estado"] = "aceptada"

        # 3) Registrar esta solicitud en la hoja 'pedidos completados'
        try:
            fila_completada = [
                solicitud_encontrada["id"],
                solicitud_encontrada.get("tipo_servicio"),
                solicitud_encontrada.get("origen"),
                solicitud_encontrada.get("destino"),
                solicitud_encontrada.get("distancia_km"),
                solicitud_encontrada.get("precio"),
                solicitud_encontrada.get("timestamp"),
                solicitud_encontrada.get("estado"),  # 'aceptada'
            ]
            ws_pedidos_completados.append_row(fila_completada)
        except Exception as e:
            app.logger.error(f"Error guardando en 'pedidos completados': {e}")

        # 4) Construir respuesta para socio.html
        respuesta = {
            "id": solicitud_encontrada["id"],
            "tipo_servicio": solicitud_encontrada.get("tipo_servicio") or "TAXI",
            "origen": solicitud_encontrada.get("origen") or "No especificado",
            "destino": solicitud_encontrada.get("destino") or "No especificado",
            "distancia_km": to_float_or_none(solicitud_encontrada.get("distancia_km")),
            "precio": to_float_or_none(solicitud_encontrada.get("precio")),
        }

        return jsonify({
            "ok": True,
            "solicitud": respuesta
        }), 200

    except Exception as e:
        app.logger.error(f"Error interno al aceptar solicitud: {e}")
        return jsonify({
            "ok": False,
            "error": "Error interno al aceptar la solicitud"
        }), 500



@app.route('/api/solicitudes/<int:solicitud_id>/aceptar', methods=['POST'])
def api_aceptar_solicitud(solicitud_id):
    """
    Marca una solicitud como 'aceptada'.
    En el futuro aquí podremos guardar el socio que la tomó.
    """
    for s in SOLICITUDES:
        if s.get("id") == solicitud_id:
            if s.get("estado") != "pendiente":
                return jsonify({
                    "ok": False,
                    "error": "La solicitud ya fue aceptada o no está disponible."
                }), 400

            s["estado"] = "aceptada"
            app.logger.info(f"Solicitud {solicitud_id} aceptada por un socio.")

            return jsonify({"ok": True, "solicitud": s}), 200

    return jsonify({
        "ok": False,
        "error": "Solicitud no encontrada."
    }), 404



if __name__ == '__main__':
    app.run(debug=True)
