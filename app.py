from flask import Flask, render_template, request
import telegram
import asyncio
import logging

app = Flask(__name__)

# Tokens de los bots y Chat ID
BOT_TOKEN_VIP = '7557496462:AAG5pa4rkbikdBYiNAEr9tuNCSDRp53yv54'
CHAT_ID = '5828174289'

# Configuración de logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[logging.StreamHandler()]
)

# Crear instancia del bot
bot_vip = telegram.Bot(token=BOT_TOKEN_VIP)

# Función asincrónica para enviar el mensaje
async def enviar_mensaje_async(mensaje):
    try:
        await bot_vip.send_message(chat_id=CHAT_ID, text=mensaje, parse_mode='Markdown')
        app.logger.debug("Mensaje enviado a Telegram con éxito.")
    except Exception as e:
        app.logger.error(f"Error al enviar mensaje a Telegram: {e}")

# Función para manejar el envío asincrónico
def enviar_mensaje(mensaje):
    asyncio.run(enviar_mensaje_async(mensaje))

# Ruta para la página principal
@app.route('/')
def principal():
    return render_template('principal.html')

# Ruta para la página Alta Gama
@app.route('/alta-gama')
def alta_gama():
    return render_template('alta_gama.html')

# Ruta para manejar la solicitud de Alta Gama
@app.route('/solicitar-alta-gama', methods=['POST'])
def solicitar_alta_gama():
    try:
        vehiculo = request.form['vehiculo']
        mensaje = f"*Solicitud de Alta Gama*\n\nVehículo solicitado: {vehiculo}"
        enviar_mensaje(mensaje)
        return render_template('gracias.html', mensaje="¡Un placer servirte! Tu vehículo llegará a la hora indicada. Gracias 😊")
    except Exception as e:
        app.logger.error(f"Error en /solicitar-alta-gama: {e}")
        return "Error al procesar la solicitud de Alta Gama.", 500

# Ruta para la página de agradecimiento
@app.route('/gracias')
def gracias():
    mensaje = request.args.get('mensaje', "¡Gracias por tu solicitud!")
    return render_template('gracias.html', mensaje=mensaje)

if __name__ == '__main__':
    app.run(debug=True)
