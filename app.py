from flask import Flask, render_template, request, redirect, url_for
import telegram
import asyncio

app = Flask(__name__)

# Configura el nuevo bot de Telegram con el token del otro bot
BOT_TOKEN = '7557496462:AAG5pa4rkbikdBYiNAEr9tuNCSDRp53yv54'  # Token actualizado del nuevo bot
CHAT_ID = '5828174289'  # Cambia este valor si deseas enviar a un chat diferente
bot = telegram.Bot(token=BOT_TOKEN)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/reservar', methods=['POST'])
def reservar():
    # Recoge los datos del formulario
    origen = request.form['origen']
    destino = request.form['destino']
    fecha = request.form['fecha']
    hora = request.form['hora']
    personas = request.form['personas']

    # Crea el mensaje de reserva
    mensaje = (f"Reserva recibida:\n"
               f"Origen: {origen}\n"
               f"Destino: {destino}\n"
               f"Fecha: {fecha}\n"
               f"Hora: {hora}\n"
               f"Personas: {personas}")

    # Define una función para enviar el mensaje de forma asíncrona
    async def enviar_mensaje():
        await bot.send_message(chat_id=CHAT_ID, text=mensaje)

    # Ejecuta la función asincrónica
    asyncio.run(enviar_mensaje())

    # Redirige al usuario a la página principal después de enviar la reserva
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
