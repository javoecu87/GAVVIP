from flask import Flask, render_template, request, send_from_directory, jsonify

import telegram
import asyncio
import logging
# import gspread


app = Flask(__name__)

# Tokens de los bots para los formularios
BOT_TOKEN_TAXI = '8146583492:AAFP-9CTNvmNR13aFxvJB6Q1WS0eBbZhAc0'
BOT_TOKEN_VIP = '7557496462:AAG5pa4rkbikdBYiNAEr9tuNCSDRp53yv54'
BOT_TOKEN_TURISMO = '8590651604:AAFXhSpGmtjNy89FBQGQ3xvXVB0t5cakZ8g'

CHAT_ID = '5828174289'  # Reemplaza con el chat ID correcto

# IDs de los chats de los grupos
CHAT_ID_TAXI = '-1002164567405'  # Grupo TAXI GAVVIP
CHAT_ID_TURISMO = '-1002164567405'  # Grupo TURISMO GAVVIP (usar el correcto cuando lo tengas)

BOT_TOKEN_REGISTRO_SOCIO = '8160209072:AAFnlNrBaML99akWHZMYdYZL7Y60udRquKA'  # Bot para formulario de socio


# Configuración de logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[logging.StreamHandler()]
)


# ================== GOOGLE SHEETS ==================
# import gspread
#
# GC_CREDS_PATH = "/etc/gavvip-credenciales.json"
# gc = gspread.service_account(filename=GC_CREDS_PATH)
#
# Hoja donde se guardan TODOS los pedidos generados por los usuarios
# sh_pedidos = gc.open('pedidos')
# ws_pedidos = sh_pedidos.sheet1     # o .worksheet('PEDIDOS') si le pusiste nombre
#
# Hoja donde se guardan los pedidos ya aceptados / terminados
# sh_pedidos_completados = gc.open('pedidos completados')
# ws_pedidos_completados = sh_pedidos_completados.sheet1   # o .worksheet('PEDIDOS COMPLETADOS')



def to_float_or_none(valor):
    """
    Convierte valor a float si es posible, si no, devuelve None.
    """
    try:
        if valor is None:
            return None
        if isinstance(valor, (int, float)):
            return float(valor)
        if isinstance(valor, str):
            v = valor.replace(',', '.')
            return float(v)
    except ValueError:
        return None


# Variable global simulando base de datos en memoria
SOLICITUDES = []
NEXT_ID_SOLICITUD = 1  # Se irá incrementando


@app.route('/registro_socio')
def registro_socio():
    return render_template('registro_socio.html')


@app.route('/verificar_socio')
def verificar_socio():
    return render_template('verificar_socio.html')



# Rutas de la ventana principal y sus botones
@app.route('/')
def ventana_emergente():
    return render_template('ventana_emergente.html')


@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/taxi')
def taxi():
    return render_template('taxi.html')


@app.route('/alta_gama')
def alta_gama():
    return render_template('alta_gama.html')


@app.route('/turismo')
def turismo():
    return render_template('turismo.html')


@app.route('/fletes')
def fletes():
    return render_template('fletes.html')


@app.route('/socio')
def socio():
    return render_template('socio.html')


@app.route('/registro_socio.html')
def mostrar_registro_socio():
    return render_template('registro_socio.html')


# Rutas de video de fondo y formularios
@app.route('/taxi-service')
def taxi_service():
    return render_template('taxi.html')


@app.route('/turismo-subventana')
def turismo_subventana():
    return render_template('turismo_subventana.html')


@app.route('/turismo-ecuador')
def turismo_ecuador():
    return render_template('turismo-ecuador.html')


@app.route('/videos/<path:filename>')
def serve_video(filename):
    return send_from_directory('videos', filename)


@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)


@app.route('/turismoecuador')
def turismoecuador():
    return render_template('turismo.html')


@app.route('/tipo_unidad')
def tipo_unidad():
    return render_template('tipo_unidad.html')


# ===================== FUNCIONES ASÍNCRONAS PARA TELEGRAM =====================

async def enviar_mensaje_telegram(bot_token, chat_id, mensaje):
    """
    Envía un mensaje a un chat de Telegram usando un bot.
    """
    bot = telegram.Bot(token=bot_token)
    await bot.send_message(chat_id=chat_id, text=mensaje)


# ===================== RUTAS PRINCIPALES: TAXI, VIP, TURISMO, FLETES =====================

@app.route('/enviar_taxi', methods=['POST'])
def enviar_taxi():
    global SOLICITUDES, NEXT_ID_SOLICITUD

    logging.debug("Solicitud /enviar_taxi recibida")

    try:
        nombre = request.form.get('nombre', 'No especificado')
        telefono = request.form.get('telefono', 'No especificado')
        direccion = request.form.get('direccion', 'No especificado')
        referencia = request.form.get('referencia', 'No especificada')
        forma_pago = request.form.get('forma_pago', 'No especificada')
        tipo_vehiculo = request.form.get('tipo_vehiculo', 'No especificado')
        tipo_servicio = request.form.get('tipo_servicio', 'TAXI')

        # 1) Crear un registro de la solicitud en memoria
        solicitud = {
            "id": NEXT_ID_SOLICITUD,
            "tipo_servicio": tipo_servicio,
            "nombre": nombre,
            "telefono": telefono,
            "direccion": direccion,
            "referencia": referencia,
            "forma_pago": forma_pago,
            "tipo_vehiculo": tipo_vehiculo,
            "estado": "pendiente",  # pendiente, aceptada, en_curso, finalizada, cancelada
        }

        SOLICITUDES.append(solicitud)
        logging.info(f"Nueva solicitud TAXI creada con ID={NEXT_ID_SOLICITUD}")
        NEXT_ID_SOLICITUD += 1

        # 2) Enviar mensaje al grupo de socios TAXI (Telegram)
        mensaje = (
            f"🚕 *NUEVA SOLICITUD TAXI*\n"
            f"ID: {solicitud['id']}\n"
            f"Nombre: {nombre}\n"
            f"Teléfono: {telefono}\n"
            f"Dirección: {direccion}\n"
            f"Referencia: {referencia}\n"
            f"Forma de pago: {forma_pago}\n"
            f"Tipo de vehículo: {tipo_vehiculo}\n"
            f"Estado: {solicitud['estado']}"
        )

        try:
            asyncio.run(
                enviar_mensaje_telegram(BOT_TOKEN_TAXI, CHAT_ID_TAXI, mensaje)
            )
        except Exception as e:
            logging.error(f"Error enviando mensaje a Telegram TAXI: {e}")

        # 3) (OPCIONAL FUTURO) Guardar en Google Sheets 'pedidos'
        # try:
        #     fila_pedidos = [
        #         solicitud["id"],
        #         solicitud["tipo_servicio"],
        #         solicitud["nombre"],
        #         solicitud["telefono"],
        #         solicitud["direccion"],
        #         solicitud["referencia"],
        #         solicitud["forma_pago"],
        #         solicitud["tipo_vehiculo"],
        #         solicitud["estado"],
        #     ]
        #     ws_pedidos.append_row(fila_pedidos)
        # except Exception as e:
        #     app.logger.error(f"Error guardando pedido en hoja 'pedidos': {e}")

        # 4) Respuesta al usuario (navegador)
        return render_template('confirmacion.html', mensaje="Solicitud TAXI enviada correctamente ✅")

    except Exception as e:
        logging.error(f"Error en /enviar_taxi: {e}")
        return render_template('error.html', mensaje="Ocurrió un error al procesar la solicitud de TAXI.")


@app.route('/enviar_vip', methods=['POST'])
def enviar_vip():
    logging.debug("Solicitud /enviar_vip recibida")

    try:
        nombre = request.form.get('nombre', 'No especificado')
        telefono = request.form.get('telefono', 'No especificado')
        direccion = request.form.get('direccion', 'No especificada')
        referencia = request.form.get('referencia', 'No especificada')
        forma_pago = request.form.get('forma_pago', 'No especificada')
        tipo_vehiculo = request.form.get('tipo_vehiculo', 'No especificado')

        mensaje = (
            f"🚗🚗🚗 | 🚕 Taxi VIP (SUVs & Vans) 🚕\n\n"
            f"👤 Nombre: {nombre}\n"
            f"📱 Teléfono: {telefono}\n"
            f"📍 Dirección de recogida: {direccion}\n"
            f"🧭 Referencias: {referencia}\n"
            f"💳 Forma de pago: {forma_pago}\n"
            f"🚗 Tipo de vehículo: {tipo_vehiculo}"
        )

        asyncio.run(
            enviar_mensaje_telegram(BOT_TOKEN_VIP, CHAT_ID_TAXI, mensaje)
        )

        return render_template('confirmacion.html', mensaje="Solicitud TAXI VIP enviada correctamente ✅")
    except Exception as e:
        logging.error(f"Error en /enviar_vip: {e}")
        return render_template('error.html', mensaje="Ocurrió un error al procesar la solicitud de TAXI VIP.")


@app.route('/enviar_turismo', methods=['POST'])
def enviar_turismo():
    logging.debug("Solicitud /enviar_turismo recibida")

    try:
        nombre = request.form.get('nombre', 'No especificado')
        telefono = request.form.get('telefono', 'No especificado')
        destino = request.form.get('destino', 'No especificado')
        fecha = request.form.get('fecha', 'No especificada')
        numero_personas = request.form.get('numero_personas', 'No especificado')
        descripcion = request.form.get('descripcion', 'No especificada')

        mensaje = (
            f"🏝️ NUEVA SOLICITUD DE TURISMO\n\n"
            f"👤 Nombre: {nombre}\n"
            f"📱 Teléfono: {telefono}\n"
            f"📍 Destino: {destino}\n"
            f"📅 Fecha: {fecha}\n"
            f"👥 Número de personas: {numero_personas}\n"
            f"📝 Descripción: {descripcion}"
        )

        asyncio.run(
            enviar_mensaje_telegram(BOT_TOKEN_TURISMO, CHAT_ID_TURISMO, mensaje)
        )

        return render_template('confirmacion.html', mensaje="Solicitud de TURISMO enviada correctamente ✅")
    except Exception as e:
        logging.error(f"Error en /enviar_turismo: {e}")
        return render_template('error.html', mensaje="Ocurrió un error al procesar la solicitud de TURISMO.")


@app.route('/enviar_fletes', methods=['POST'])
def enviar_fletes():
    logging.debug("Solicitud /enviar_fletes recibida")

    try:
        nombre = request.form.get('nombre', 'No especificado')
        telefono = request.form.get('telefono', 'No especificado')
        direccion_recogida = request.form.get('direccion_recogida', 'No especificada')
        direccion_entrega = request.form.get('direccion_entrega', 'No especificada')
        tipo_carga = request.form.get('tipo_carga', 'No especificada')
        peso_aproximado = request.form.get('peso_aproximado', 'No especificado')

        mensaje = (
            f"🚚 NUEVA SOLICITUD DE FLETES\n\n"
            f"👤 Nombre: {nombre}\n"
            f"📱 Teléfono: {telefono}\n"
            f"📍 Dirección de recogida: {direccion_recogida}\n"
            f"📍 Dirección de entrega: {direccion_entrega}\n"
            f"📦 Tipo de carga: {tipo_carga}\n"
            f"⚖️ Peso aproximado: {peso_aproximado}"
        )

        asyncio.run(
            enviar_mensaje_telegram(BOT_TOKEN_TAXI, CHAT_ID_TAXI, mensaje)
        )

        return render_template('confirmacion.html', mensaje="Solicitud de FLETES enviada correctamente ✅")
    except Exception as e:
        logging.error(f"Error en /enviar_fletes: {e}")
        return render_template('error.html', mensaje="Ocurrió un error al procesar la solicitud de FLETES.")


# ===================== REGISTRO DE SOCIOS CONDUCTORES =====================

@app.route('/enviar_registro_socio', methods=['POST'])
def enviar_registro_socio():
    logging.debug("Solicitud /enviar_registro_socio recibida")

    try:
        nombres = request.form.get('nombres', 'No especificado')
        apellidos = request.form.get('apellidos', 'No especificado')
        tipo_vehiculo = request.form.get('tipo_vehiculo', 'No especificado')
        placas = request.form.get('placas', 'No especificadas')
        licencia = request.form.get('licencia', 'No especificada')
        telefono = request.form.get('telefono', 'No especificado')
        correo = request.form.get('correo', 'No especificado')
        comentario = request.form.get('comentario', 'Sin comentarios adicionales')

        mensaje = (
            f"🚖 NUEVA SOLICITUD DE SOCIO CONDUCTOR 🚖\n\n"
            f"👤 Nombres: {nombres}\n"
            f"👤 Apellidos: {apellidos}\n"
            f"🚗 Tipo de vehículo: {tipo_vehiculo}\n"
            f"🔢 Placas: {placas}\n"
            f"🪪 Licencia: {licencia}\n"
            f"📱 Teléfono: {telefono}\n"
            f"📧 Correo: {correo}\n"
            f"📝 Comentario: {comentario}\n\n"
            f"🔍 Verificar la información y aprobar o rechazar al socio."
        )

        asyncio.run(
            enviar_mensaje_telegram(BOT_TOKEN_REGISTRO_SOCIO, CHAT_ID_TAXI, mensaje)
        )

        return render_template('confirmacion.html', mensaje="Registro de socio enviado para verificación ✅")
    except Exception as e:
        logging.error(f"Error en /enviar_registro_socio: {e}")
        return render_template('error.html', mensaje="Ocurrió un error al procesar el registro de socio.")


# ===================== API PARA SOCIOS (LECTURA Y ACEPTACIÓN DE SOLICITUDES) =====================

@app.route('/api/solicitudes/pendientes', methods=['GET'])
def api_solicitudes_pendientes():
    """
    Devuelve todas las solicitudes en estado 'pendiente'.
    Esto será consumido por socio.html para mostrar la lista.
    """
    pendientes = [s for s in SOLICITUDES if s.get("estado") == "pendiente"]
    return jsonify({
        "ok": True,
        "solicitudes": pendientes
    }), 200


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
