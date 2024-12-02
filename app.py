from flask import Flask, render_template, redirect, url_for, request
import requests
import logging
import asyncio

app = Flask(__name__)

# Configuración de tokens y chat IDs
BOT_TOKEN_TAXI = '8146583492:AAFP-9CTNvmNR13aFxvJB6Q1WS0eBbZhAc0'
BOT_TOKEN_VIP = '7557496462:AAG5pa4rkbikdBYiNAEr9tuNCSDRp53yv54'
CHAT_ID = '5828174289'

# Configuración de logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(message)s')

# Función asincrónica para enviar mensajes
async def enviar_mensaje_async(bot_token, mensaje):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": mensaje, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            logging.info("Mensaje enviado con éxito.")
        else:
            logging.error(f"Error al enviar mensaje: {response.status_code} - {response.text}")
    except Exception as e:
        logging.error(f"Error en la conexión: {e}")

# Función para manejar el envío asincrónico
def enviar_mensaje(bot_token, mensaje):
    asyncio.run(enviar_mensaje_async(bot_token, mensaje))

# Rutas principales
@app.route('/')
def principal():
    return render_template('principal.html')

@app.route('/emergente')
def emergente():
    return render_template('emergente.html')

@app.route('/taxi-service')
def taxi_service():
    return render_template('taxi.html')

@app.route('/turismo')
def turismo():
    return render_template('turismo.html')

@app.route('/alta-gama')
def alta_gama():
    return render_template('alta_gama.html')

@app.route('/fletes')
def fletes():
    return render_template('fletes.html')

@app.route('/apoyo-hoteles')
def apoyo_hoteles():
    return render_template('apoyo_hoteles.html')

# Manejo de formularios y redirecciones
@app.route('/enviar-taxi', methods=['POST'])
def enviar_taxi():
    nombre = request.form.get('nombre')
    telefono = request.form.get('telefono')
    lugar_recogida = request.form.get('lugar_recogida')
    destino = request.form.get('destino')
    pasajeros = request.form.get('pasajeros')

    mensaje = f"""
    *Solicitud de Taxi*
    Nombre: {nombre}
    Teléfono: {telefono}
    Lugar de recogida: {lugar_recogida}
    Destino: {destino}
    Pasajeros: {pasajeros}
    """
    enviar_mensaje(BOT_TOKEN_TAXI, mensaje)
    return redirect(url_for('principal'))

@app.route('/enviar-vip', methods=['POST'])
def enviar_vip():
    nombre = request.form.get('nombre')
    telefono = request.form.get('telefono')
    lugar_recogida = request.form.get('lugar_recogida')
    tiempo = request.form.get('tiempo')

    mensaje = f"""
    *Solicitud de Alta Gama*
    Nombre: {nombre}
    Teléfono: {telefono}
    Lugar de recogida: {lugar_recogida}
    Tiempo requerido: {tiempo}
    """
    enviar_mensaje(BOT_TOKEN_VIP, mensaje)
    return render_template('gracias.html', mensaje="Tu solicitud fue enviada con éxito.")

@app.route('/error')
def error():
    return render_template('error.html')

# Ruta de prueba
@app.route('/test')
def test():
    return "Aplicación funcionando correctamente."

if __name__ == '__main__':
    app.run(debug=True)
