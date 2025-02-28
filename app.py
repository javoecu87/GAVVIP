from flask import Flask, render_template, request, send_from_directory
import telegram
import asyncio
import logging

app = Flask(__name__)

# Tokens de los bots para los formularios
BOT_TOKEN_TAXI = '8146583492:AAG5pa4rkbikdBYiNAEr9tuNCSDRp53yv54'
BOT_TOKEN_VIP = '7557496462:AAG5pa4rkbikdBYiNAEr9tuNCSDRp53yv54'
CHAT_ID = '5828174289'  # Reemplaza con el chat ID correcto

# Configuración de logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[logging.StreamHandler()]
)

# Función asincrónica para enviar el mensaje a Telegram
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

# Ruta para servir archivos en static/images/
@app.route('/static/images/<path:filename>')
def serve_images(filename):
    return send_from_directory('static/images', filename)

@app.route('/fletes-mudanzas')
def fletes_mudanzas():
    return render_template('fletes_mudanzas.html')

# Procesar formulario de Fletes y Mudanzas
@app.route('/solicitar-fletes-mudanzas', methods=['POST'])
def solicitar_fletes_mudanzas():
    try:
        nombre = request.form.get('nombre')
        telefono = request.form.get('telefono')
        origen = request.form.get('origen')
        destino = request.form.get('destino')
        detalles = request.form.get('detalles')

        mensaje = (
            "*Solicitud de Fletes y Mudanzas*\n\n"
            f"👤 Nombre: {nombre}\n"
            f"📞 Teléfono: {telefono}\n"
            f"📍 Origen: {origen}\n"
            f"🎯 Destino: {destino}\n"
            f"📋 Detalles: {detalles}"
        )

        # Enviar mensaje a Telegram
        enviar_mensaje(mensaje, BOT_TOKEN_VIP)

        return render_template('success.html', mensaje="¡Gracias! Tu solicitud de Fletes y Mudanzas ha sido enviada.")
    except Exception as e:
        app.logger.error(f"Error en /solicitar-fletes-mudanzas: {e}")
        return "Error al procesar la solicitud de Fletes y Mudanzas.", 500

# Ruta para la subventana de Turismo
@app.route('/turismo-subventana')
def turismo_subventana():
    return render_template('turismo_subventana.html')

# Ruta para "Turismo Ecuador"
@app.route('/turismo-ecuador')
def turismo_ecuador():
    return render_template('turismo-ecuador.html')

# Ruta para "Ecuador 420"
@app.route('/ecuador-420')
def ecuador_420():
    return render_template('ecuador-420.html')

# Ruta para manejar la solicitud de Turismo Ecuador
@app.route('/solicitar-turismo-ecuador', methods=['POST'])
def solicitar_turismo_ecuador():
    try:
        nombre = request.form.get('nombre')
        telefono = request.form.get('telefono')
        origen = request.form.get('origen')
        destino = request.form.get('destino')
        fecha = request.form.get('fecha')

        mensaje = (
            "*Solicitud de Turismo Ecuador*\n\n"
            f"👤 Nombre: {nombre}\n"
            f"📞 Teléfono: {telefono}\n"
            f"📍 Origen: {origen}\n"
            f"🎯 Destino: {destino}\n"
            f"📅 Fecha: {fecha}"
        )

        enviar_mensaje(mensaje, BOT_TOKEN_TAXI, CHAT_ID)  
        return render_template('success.html', mensaje="¡Gracias! Tu solicitud de Turismo Ecuador ha sido enviada.")
    except Exception as e:
        app.logger.error(f"Error en /solicitar-turismo-ecuador: {e}")
        return "Error al procesar la solicitud de Turismo Ecuador.", 500

# Ruta para manejar la solicitud de Ecuador 420
@app.route('/solicitar-ecuador-420', methods=['POST'])
def solicitar_ecuador_420():
    try:
        nombre = request.form.get('nombre')
        telefono = request.form.get('telefono')
        origen = request.form.get('origen')
        destino = request.form.get('destino')
        fecha = request.form.get('fecha')

        mensaje = (
            "*Solicitud de Ecuador 420*\n\n"
            f"👤 Nombre: {nombre}\n"
            f"📞 Teléfono: {telefono}\n"
            f"📍 Origen: {origen}\n"
            f"🎯 Destino: {destino}\n"
            f"📅 Fecha: {fecha}"
        )

        enviar_mensaje(mensaje, BOT_TOKEN_TAXI, CHAT_ID)  
        return render_template('success.html', mensaje="¡Gracias! Tu solicitud de Ecuador 420 ha sido enviada.")
    except Exception as e:
        app.logger.error(f"Error en /solicitar-ecuador-420: {e}")
        return "Error al procesar la solicitud de Ecuador 420.", 500

# Ruta para la página principal
@app.route('/principal')
def principal():
    return render_template('principal.html')

# Ruta para la ventana emergente
@app.route('/ventana-emergente')
def ventana_emergente():
    return render_template('emergente.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
