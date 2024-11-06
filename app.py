from flask import Flask, render_template, request
import telegram
import asyncio
import logging

app = Flask(__name__)

# Tokens de los bots para los formularios de Taxi y TAXI VIP SUVS & VANS
BOT_TOKEN_TAXI = '8146583492:AAFP-9CTNvmNR13aFxvJB6Q1WS0eBbZhAc0'
BOT_TOKEN_VIP = '7557496462:AAG5pa4rkbikdBYiNAEr9tuNCSDRp53yv54'
CHAT_ID = '5828174289'  # Reemplaza con el chat ID correcto para ambos bots si es necesario

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

# Ruta para la ventana principal
@app.route('/')
def principal():
    return render_template('principal.html')

# Ruta para el formulario de Taxi
@app.route('/taxi-service')
def taxi_service():
    return render_template('taxi.html')

# Ruta para procesar el formulario de Taxi y enviar el mensaje al bot de Taxi
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
            f"Nombre: {nombre}\n"
            f"Teléfono: {telefono}\n"
            f"Lugar de recogida: {lugar_recogida}\n"
            f"Destino: {destino}\n"
            f"Número de pasajeros: {pasajeros}"
        )

        enviar_mensaje(mensaje, BOT_TOKEN_TAXI)
        return render_template('gracias.html', mensaje="¡Gracias! Su solicitud de taxi ha sido enviada.")
    except Exception as e:
        app.logger.error(f"Error en /solicitar-taxi: {e}")
        return "Error al procesar la solicitud de taxi.", 500

# Ruta para el formulario TAXI VIP SUVS & VANS
@app.route('/reservar-formulario')
def reservar_formulario():
    return render_template('index.html')

# Ruta para procesar el formulario TAXI VIP SUVS & VANS y enviar el mensaje al bot
@app.route('/reservar', methods=['POST'])
def reservar():
    try:
        nombre = request.form['nombre']
        telefono = request.form['telefono']
        origen = request.form['origen']
        destino = request.form['destino']
        fecha = request.form['fecha']
        hora = request.form['hora']
        personas = request.form['personas']

        mensaje = (
            "*Solicitud de TAXI VIP SUVS & VANS*\n\n"
            f"Nombre: {nombre}\n"
            f"Teléfono: {telefono}\n"
            f"Origen: {origen}\n"
            f"Destino: {destino}\n"
            f"Fecha: {fecha}\n"
            f"Hora: {hora}\n"
            f"Personas: {personas}"
        )

        enviar_mensaje(mensaje, BOT_TOKEN_VIP)
        return render_template('gracias.html', mensaje="¡Gracias! Su reservación está confirmada.")
    except Exception as e:
        app.logger.error(f"Error en /reservar: {e}")
        return "Error al procesar la reserva.", 500

if __name__ == '__main__':
    app.run(debug=True)
