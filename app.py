from flask import Flask, render_template, request, send_from_directory, jsonify
import telegram
import asyncio
import logging
import random

app = Flask(__name__)

# Tokens de los bots para los formularios
BOT_TOKEN_TAXI = '8146583492:AAFP-9CTNvmNR13aFxvJB6Q1WS0eBbZhAc0'
BOT_TOKEN_VIP = '7557496462:AAG5pa4rkbikdBYiNAEr9tuNCSDRp53yv54'
CHAT_ID = '5828174289'  # Reemplaza con el chat ID correcto

# Configuración de logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[logging.StreamHandler()]
)

# Función asincrónica para enviar el mensaje
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

@app.route('/static/images/<path:filename>')
def serve_images(filename):
    return send_from_directory('static/images', filename)

@app.route('/fletes-mudanzas')
def fletes_mudanzas():
    return render_template('fletes_mudanzas.html')

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

        return render_template('gracias.html')
    except Exception as e:
        app.logger.error(f"Error en /solicitar-fletes-mudanzas: {e}")
        return "Error al procesar la solicitud de Fletes y Mudanzas.", 500

@app.route('/apoyo-hoteles')
def apoyo_hoteles():
    return render_template('apoyo_hoteles.html')

@app.route('/alta-gama')
def alta_gama():
    return render_template('alta_gama.html')

@app.route('/')
def ventana_emergente():
    return render_template('emergente.html')

@app.route('/principal')
def principal():
    return render_template('principal.html')

@app.route('/taxi-service')
def taxi_service():
    return render_template('taxi.html')

@app.route('/solicitar-taxi', methods=['POST'])
def solicitar_taxi():
    try:
        nombre = request.form.get('nombre')
        telefono = request.form.get('telefono')
        lugar_recogida = request.form.get('lugar_recogida')
        destino = request.form.get('destino')
        pasajeros = request.form.get('pasajeros')

        mensaje = (
            "*Solicitud de Taxi*\n\n"
            f"👤 Nombre: {nombre}\n"
            f"📞 Teléfono: {telefono}\n"
            f"📍 Lugar de Recogida: {lugar_recogida}\n"
            f"🎯 Destino: {destino}\n"
            f"👥 Pasajeros: {pasajeros}"
        )

        enviar_mensaje(mensaje, BOT_TOKEN_TAXI)

        return render_template('gracias.html')
    except Exception as e:
        app.logger.error(f"Error en /solicitar-taxi: {e}")
        return "Error al procesar la solicitud de taxi.", 500

### 🔹 MEJORAS AÑADIDAS (SIN ELIMINAR NADA) 🔹 ###
# Diccionario para almacenar viajes activos
viajes_activos = {}

# Ruta para manejar reservas desde index.html y enviar mensaje al bot
@app.route('/reservar', methods=['POST'])
def reservar():
    try:
        nombre = request.form.get('nombre')
        telefono = request.form.get('telefono')
        origen = request.form.get('origen')
        destino = request.form.get('destino')

        viaje_id = str(len(viajes_activos) + 1)
        viajes_activos[viaje_id] = {
            "nombre": nombre,
            "telefono": telefono,
            "origen": origen,
            "destino": destino,
            "estado": "pendiente",
            "conductor": None
        }

        mensaje = (
            "*Nueva Solicitud de Viaje*\n\n"
            f"👤 Nombre: {nombre}\n"
            f"📞 Teléfono: {telefono}\n"
            f"📍 Origen: {origen}\n"
            f"🎯 Destino: {destino}"
        )

        # Enviar mensaje a Telegram
        enviar_mensaje(mensaje, BOT_TOKEN_TAXI)

        return jsonify({"mensaje": "Solicitud recibida", "viaje_id": viaje_id})
    except Exception as e:
        app.logger.error(f"Error en /reservar: {e}")
        return jsonify({"error": "Error al procesar la solicitud"}), 500

# Ruta para obtener la ubicación en tiempo real del vehículo
@app.route('/ubicacion-vehiculo')
def ubicacion_vehiculo():
    try:
        vehiculo_lat = 19.4500 + (random.uniform(-0.001, 0.001))  
        vehiculo_lng = -99.1700 + (random.uniform(-0.001, 0.001))

        return jsonify({"lat": vehiculo_lat, "lng": vehiculo_lng})
    except Exception as e:
        app.logger.error(f"Error en /ubicacion-vehiculo: {e}")
        return jsonify({"error": "Error al obtener la ubicación"}), 500

# Ruta para asignar un conductor a un viaje
@app.route('/asignar-conductor/<viaje_id>')
def asignar_conductor(viaje_id):
    try:
        if viaje_id in viajes_activos:
            viajes_activos[viaje_id]["conductor"] = {
                "nombre": "Carlos Gómez",
                "telefono": "+52 555-123-4567"
            }

            mensaje = (
                f"✅ *Viaje Aceptado*\n\n"
                f"👤 Conductor: {viajes_activos[viaje_id]['conductor']['nombre']}\n"
                f"📞 Teléfono: {viajes_activos[viaje_id]['conductor']['telefono']}\n"
                f"📍 Origen: {viajes_activos[viaje_id]['origen']}\n"
                f"🎯 Destino: {viajes_activos[viaje_id]['destino']}"
            )

            enviar_mensaje(mensaje, BOT_TOKEN_TAXI)

            return jsonify(viajes_activos[viaje_id])
        return jsonify({"error": "Viaje no encontrado"}), 404
    except Exception as e:
        app.logger.error(f"Error en /asignar-conductor: {e}")
        return jsonify({"error": "Error al asignar conductor"}), 500

if __name__ == '__main__':
    app.run(debug=True)
