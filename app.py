from flask import Flask, render_template, request
import telegram
import asyncio
import logging

app = Flask(__name__)

# Tokens de los bots
BOT_TOKEN_TAXI = '8146583492:AAFP-9CTNvmNR13aFxvJB6Q1WS0eBbZhAc0'
BOT_TOKEN_VIP = '7557496462:AAG5pa4rkbikdBYiNAEr9tuNCSDRp53yv54'
CHAT_ID = '5828174289'  # Reemplaza con el chat ID correcto

# Configuración de logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[logging.StreamHandler()]
)

# Función asincrónica para enviar mensaje
async def enviar_mensaje_async(mensaje, token):
    bot = telegram.Bot(token=token)
    try:
        await bot.send_message(chat_id=CHAT_ID, text=mensaje, parse_mode='Markdown')
        app.logger.debug("Mensaje enviado a Telegram con éxito")
    except Exception as e:
        app.logger.error(f"Error al enviar mensaje a Telegram: {e}")

# Función para ejecutar el envío de manera asincrónica
def enviar_mensaje(mensaje, token):
    asyncio.run(enviar_mensaje_async(mensaje, token))

# Rutas

# Ruta para la ventana emergente
@app.route('/')
def emergente():
    return render_template('emergente.html')

# Ruta para la página principal
@app.route('/principal')
def principal():
    return render_template('principal.html')

# Ruta para el servicio de Taxi
@app.route('/taxi-service')
def taxi_service():
    return render_template('taxi.html')

# Ruta para manejar el formulario de Taxi
@app.route('/solicitar-taxi', methods=['POST'])
def solicitar_taxi():
    try:
        nombre = request.form['nombre']
        telefono = request.form['telefono']
        lugar_recogida = request.form['lugar_recogida']
        destino = request.form['destino']
        pasajeros = request.form['pasajeros']

        mensaje = (
            "*Solicitud de Taxi*\n\n"
            f"👤 Nombre: {nombre}\n"
            f"📞 Teléfono: {telefono}\n"
            f"📍 Lugar de recogida: {lugar_recogida}\n"
            f"🎯 Destino: {destino}\n"
            f"👥 Pasajeros: {pasajeros}"
        )

        enviar_mensaje(mensaje, BOT_TOKEN_TAXI)
        return render_template('success.html', mensaje="¡Gracias! Su solicitud de taxi ha sido enviada.")
    except Exception as e:
        app.logger.error(f"Error en /solicitar-taxi: {e}")
        return "Error al procesar la solicitud de taxi.", 500

# Ruta para Turismo Local y Nacional
@app.route('/turismo')
def turismo():
    return render_template('turismo.html')

# Ruta para Alta Gama
@app.route('/alta-gama')
def alta_gama():
    return render_template('alta_gama.html')

# Ruta para Fletes y Mudanzas
@app.route('/fletes-mudanzas')
def fletes_mudanzas():
    return render_template('fletes_mudanzas.html')

# Ruta para Apoyo Hoteles
@app.route('/apoyo-hoteles')
def apoyo_hoteles():
    return render_template('apoyo_hoteles.html')

if __name__ == '__main__':
    app.run(debug=True)
