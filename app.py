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

# Función asincrónica para enviar mensajes a Telegram
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

# Ruta para servir imágenes estáticas
@app.route('/static/images/<path:filename>')
def serve_images(filename):
    return send_from_directory('static/images', filename)

# Rutas originales
@app.route('/fletes-mudanzas')
def fletes_mudanzas():
    return render_template('fletes_mudanzas.html')

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

# ✅ Ruta para manejar la solicitud de taxi y pasar coordenadas a gracias.html
@app.route('/solicitar-taxi', methods=['POST'])
def solicitar_taxi():
    try:
        nombre = request.form.get('nombre')
        telefono = request.form.get('telefono')
        origen = request.form.get('origen')
        destino = request.form.get('destino')

        # Coordenadas de ejemplo (deben ser dinámicas más adelante)
        cliente_lat = -0.1762122  
        cliente_lng = -78.4829369 
        vehiculo_lat = -0.1750100  
        vehiculo_lng = -78.3020300  

        mensaje = (
            "*Solicitud de Taxi*\n\n"
            f"👤 Nombre: {nombre}\n"
            f"📞 Teléfono: {telefono}\n"
            f"📍 Origen: {origen}\n"
            f"🎯 Destino: {destino}"
        )

        # Enviar mensaje a Telegram
        enviar_mensaje(mensaje, BOT_TOKEN_TAXI)

        return render_template('gracias.html',
                               cliente_latitud=cliente_lat,
                               cliente_longitud=cliente_lng,
                               vehiculo_latitud=vehiculo_lat,
                               vehiculo_longitud=vehiculo_lng)
    except Exception as e:
        app.logger.error(f"Error en /solicitar-taxi: {e}")
        return jsonify({"error": "Error al procesar la solicitud de taxi"}), 500

if __name__ == '__main__':
    app.run(debug=True)
