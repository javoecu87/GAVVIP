from flask import Flask, render_template, request, redirect, url_for
import requests

app = Flask(__name__)

# Configuración de los tokens y chat ID para Telegram
BOT_TOKEN_TAXI = '8146583492:AAFP-9CTNvmNR13aFxvJB6Q1WS0eBbZhAc0'
BOT_TOKEN_VIP = '7557496462:AAG5pa4rkbikdBYiNAEr9tuNCSDRp53yv54'
CHAT_ID = '5828174289'

# Función para enviar mensajes a Telegram
def enviar_mensaje(bot_token, mensaje):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": mensaje,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print("Mensaje enviado con éxito.")
        else:
            print(f"Error al enviar el mensaje: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Error en la conexión: {e}")

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

    return render_template('taxi.html')

# Ruta para Turismo Local y Nacional
@app.route('/turismo', methods=['GET', 'POST'])
def turismo():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        telefono = request.form.get('telefono')
        lugar_recogida = request.form.get('lugar_recogida')

        mensaje = f"""
        *Solicitud de Turismo*
        Nombre: {nombre}
        Teléfono: {telefono}
        Lugar de recogida: {lugar_recogida}
        """
        enviar_mensaje(BOT_TOKEN_VIP, mensaje)
        return redirect(url_for('principal'))

    return render_template('turismo.html')

# Ruta para Alta Gama
@app.route('/alta-gama', methods=['GET', 'POST'])
def alta_gama():
    if request.method == 'POST':
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
        return redirect(url_for('principal'))

    return render_template('alta_gama.html')

# Ruta para Fletes y Mudanzas
@app.route('/fletes-mudanzas', methods=['GET', 'POST'])
def fletes_mudanzas():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        telefono = request.form.get('telefono')
        tipo_servicio = request.form.get('tipo_servicio')

        mensaje = f"""
        *Solicitud de Fletes y Mudanzas*
        Nombre: {nombre}
        Teléfono: {telefono}
        Tipo de servicio: {tipo_servicio}
        """
        enviar_mensaje(BOT_TOKEN_VIP, mensaje)
        return redirect(url_for('principal'))

    return render_template('fletes_mudanzas.html')

# Ruta para Apoyo Hoteles
@app.route('/apoyo-hoteles', methods=['GET', 'POST'])
def apoyo_hoteles():
    if request.method == 'POST':
        codigo = request.form.get('codigo')
        if codigo == '515' or codigo == '122' or codigo == '155':
            return redirect(url_for('principal'))
        else:
            return "Código incorrecto. Inténtalo de nuevo."

    return render_template('apoyo_hoteles.html')

if __name__ == '__main__':
    app.run(debug=True)
