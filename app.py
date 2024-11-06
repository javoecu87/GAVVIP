from flask import Flask, render_template, request
import telegram
import asyncio
import logging

app = Flask(__name__)

# Token del nuevo bot para el botón "Taxi"
BOT_TOKEN_TAXI = '8146583492:AAFP-9CTNvmNR13aFxvJB6Q1WS0eBbZhAc0'
CHAT_ID = '5828174289'  # Asegúrate de que sea el chat ID correcto o ajusta si es necesario

# Configuración de logging para asegurar la salida en consola
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

# Ruta para procesar la solicitud de taxi
@app.route('/solicitar-taxi', methods=['POST'])
def solicitar_taxi():
    try:
        nombre = request.form['nombre']
        telefono = request.form['telefono']
        ubicacion = request.form['ubicacion']
        destino = request.form.get('destino', 'No especificado')
        observaciones = request.form.get('observaciones', 'No especificadas')

        mensaje = (
            "*Solicitud de Taxi*\n\n"
            f"Nombre: {nombre}\n"
            f"Teléfono: {telefono}\n"
            f"Ubicación: {ubicacion}\n"
            f"Destino: {destino}\n"
            f"Observaciones: {observaciones}"
        )

        # Envía el mensaje usando el token del nuevo bot
        enviar_mensaje(mensaje, BOT_TOKEN_TAXI)
        app.logger.debug("Redirigiendo a página de agradecimiento.")
        return render_template('gracias.html', mensaje="¡Gracias! Su solicitud de taxi ha sido enviada.")
    except Exception as e:
        app.logger.error(f"Error en /solicitar-taxi: {e}")
        return "Error al procesar la solicitud de taxi.", 500

# (Las demás rutas y configuraciones permanecen igual)
