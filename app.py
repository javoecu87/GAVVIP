from flask import Flask, render_template, request, redirect, url_for
import telegram

app = Flask(__name__)

# Configura tu bot de Telegram
BOT_TOKEN = '7557496462:AAG5pa4rkbikdBYiNAEr9tuNCSDRp53yv54'
CHAT_ID = '5828174289'  # Chat ID proporcionado
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

    # Envía un mensaje de notificación a Telegram
    mensaje = (f"Reserva recibida:\n"
               f"Origen: {origen}\n"
               f"Destino: {destino}\n"
               f"Fecha: {fecha}\n"
               f"Hora: {hora}\n"
               f"Personas: {personas}")
    bot.send_message(chat_id=CHAT_ID, text=mensaje)

    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
