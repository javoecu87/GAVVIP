from flask import Flask, render_template, request, redirect, url_for
import telegram
import asyncio
import logging

app = Flask(__name__)

# Configura el bot de Telegram
BOT_TOKEN = '7557496462:AAG5pa4rkbikdBYiNAEr9tuNCSDRp53yv54'
CHAT_ID = '5828174289'
bot = telegram.Bot(token=BOT_TOKEN)

# Configuración de logging para ver mensajes de depuración en la consola
logging.basicConfig(level=logging.DEBUG)

# Ruta para la ventana principal
@app.route('/')
def principal():
    return render_template('principal.html')

# Ruta para el servicio de Taxi
@app.route('/taxi-service')
def taxi_service():
    return render_template('taxi.html')

# Ruta para el formulario de Quito Tour VIP
@app.route('/reservar-formulario')
def reservar_formulario():
    return render_template('index.html')

# Función para enviar el mensaje
def enviar_mensaje(mensaje):
    try:
        asyncio.run(bot.send_message(chat_id=CHAT_ID, text=mensaje, parse_mode='Markdown'))
        app.logger.debug("Mensaje enviado a Telegram con éxito")
    except Exception as e:
        app.logger.error(f"Error al enviar mensaje a Telegram: {e}")

# Ruta para procesar la solicitud de taxi
@app.route('/solicitar-taxi', methods=['POST'])
def solicitar_taxi():
    nombre = request.form['nombre']
    telefono = request.form['telefono']
    ubicacion = request.form['ubicacion']
    destino = request.form.get('destino', 'No especificado')
    observaciones = request.form.get('observaciones', 'No especificadas')

    mensaje = (
        "🚖 *Solicitud de Taxi*\n\n"
        f"👤 *Nombre:* {nombre}\n"
        f"📞 *Teléfono:* {telefono}\n"
        f"📍 *Ubicación:* {ubicacion}\n"
        f"➡️ *Destino:* {destino}\n"
        f"📝 *Observaciones:* {observaciones}"
    )

    enviar_mensaje(mensaje)

    return render_template('gracias.html', mensaje="¡Gracias! Su solicitud de taxi ha sido enviada.")

# Ruta para procesar el formulario de reserva de Quito Tour VIP
@app.route('/reservar', methods=['POST'])
def reservar():
    app.logger.debug("Formulario recibido en /reservar")

    try:
        nombre = request.form['nombre']
        telefono = request.form['telefono']
        origen = request.form['origen']
        destino = request.form['destino']
        fecha = request.form['fecha']
        hora = request.form['hora']
        personas = request.form['personas']
        app.logger.debug(f"Datos recibidos: Nombre={nombre}, Teléfono={telefono}, Origen={origen}, Destino={destino}, Fecha={fecha}, Hora={hora}, Personas={personas}")
    except Exception as e:
        app.logger.error(f"Error al recoger los datos del formulario: {e}")
        return "Error al procesar el formulario", 500

    mensaje = (
        "🚌 *Reserva de Quito Tour VIP*\n\n"
        f"👤 *Nombre:* {nombre}\n"
        f"📞 *Teléfono:* {telefono}\n"
        f"📍 *Origen:* {origen}\n"
        f"➡️ *Destino:* {destino}\n"
        f"📅 *Fecha:* {fecha}\n"
      
