from flask import Flask, render_template, request, redirect, url_for
import requests
import telegram
import asyncio
import logging

app = Flask(__name__)

# Tokens para los bots de Telegram
BOT_TOKEN_TAXI = '8146583492:AAFP-9CTNvmNR13aFxvJB6Q1WS0eBbZhAc0'
BOT_TOKEN_VIP = '7557496462:AAG5pa4rkbikdBYiNAEr9tuNCSDRp53yv54'
CHAT_ID = '5828174289'  # Reemplaza con el chat ID correcto para ambos bots si es necesario

# Ruta para la ventana emergente
@app.route('/')
def emergente():
    return render_template('emergente.html')

# Ruta para la página principal
@app.route('/principal')
def principal():
    return render_template('principal.html')

# Ruta para el servicio de Taxi
@app.route('/taxi-service', methods=['GET', 'POST'])
def taxi_service():
    if request.method == 'POST':
        data = {
            'Nombre': request.form['nombre'],
            'Origen': request.form['origen'],
            'Destino': request.form['destino']
        }
        send_message(data, BOT_TOKEN_TAXI)
        return render_template('success.html', mensaje="¡Tu solicitud de taxi ha sido enviada!")
    return render_template('taxi.html')

# Ruta para Turismo Local y Nacional
@app.route('/turismo', methods=['GET', 'POST'])
def turismo():
    if request.method == 'POST':
        data = {
            'Nombre': request.form['nombre'],
            'Destino': request.form['destino'],
            'Fecha': request.form['fecha']
        }
        send_message(data, BOT_TOKEN_VIP)
        return render_template('success.html', mensaje="¡Tu solicitud de turismo ha sido enviada!")
    return render_template('turismo.html')

# Ruta para Alta Gama
@app.route('/alta-gama', methods=['GET', 'POST'])
def alta_gama():
    if request.method == 'POST':
        data = {
            'Nombre': request.form['nombre'],
            'Vehículo': request.form['vehiculo'],
            'Lugar de Recogida': request.form['recogida'],
            'Tiempo': request.form['tiempo']
        }
        send_message(data, BOT_TOKEN_VIP)
        return render_template('success.html', mensaje="¡Tu solicitud de vehículo de alta gama ha sido enviada!")
    return render_template('alta_gama.html')

# Ruta para Fletes y Mudanzas
@app.route('/fletes-mudanzas', methods=['GET', 'POST'])
def fletes_mudanzas():
    if request.method == 'POST':
        data = {
            'Nombre': request.form['nombre'],
            'Origen': request.form['origen'],
            'Destino': request.form['destino'],
            'Fecha': request.form['fecha']
        }
        send_message(data, BOT_TOKEN_VIP)
        return render_template('success.html', mensaje="¡Tu solicitud de fletes y mudanzas ha sido enviada!")
    return render_template('fletes_mudanzas.html')

# Ruta para Apoyo Hoteles
@app.route('/apoyo-hoteles', methods=['GET', 'POST'])
def apoyo_hoteles():
    if request.method == 'POST':
        codigo = request.form['codigo']
        if codigo in ['515', '122', '155']:
            return render_template('apoyo_hoteles_form.html')
        else:
            return render_template('error.html', mensaje="Código incorrecto. Intenta de nuevo.")
    return render_template('apoyo_hoteles.html')

# Función para enviar mensajes a Telegram
def send_message(data, token):
    chat_id = '@tu_canal'  # Cambia por el nombre de tu canal o chat_id
    mensaje = "\n".join([f"{key}: {value}" for key, value in data.items()])
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, data={'chat_id': chat_id, 'text': mensaje})

if __name__ == '__main__':
    app.run(debug=True)
