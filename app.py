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

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/reservar', methods=['POST'])
def reservar():
    app.logger.debug("Formulario recibido en /reservar")

    # Recoge los datos del formulario
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

    # Crea el mensaje de reserva
    mensaje = (f"Reserva recibida:\n"
               f"Nombre: {nombre}\n"
               f"Teléfono: {telefono}\n"
               f"Origen: {origen}\n"
               f"Destino: {destino}\n"
               f"Fecha: {fecha}\n"
               f"Hora: {hora}\n"
               f"Personas: {personas}")

    # Define una función para enviar el mensaje
    async def enviar_mensaje():
        try:
            await bot.send_message(chat_id=CHAT_ID, text=mensaje)
            app.logger.debug("Mensaje enviado a Telegram con éxito")
        except Exception as e:
            app.logger.error(f"Error al enviar mensaje a Telegram: {e}")

    # Ejecuta la función en un executor sin cerrar el bucle de eventos
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, lambda: asyncio.run(enviar_mensaje()))

    # Redirige al usuario a la página principal después de enviar la reserva
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
