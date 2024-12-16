from flask import Flask, render_template, request, redirect, url_for
import telegram
import asyncio
import logging

app = Flask(__name__)

# Tokens de los bots para los formularios
BOT_TOKEN_TAXI = '8146583492:AAFP-9CTNvmNR13aFxvJB6Q1WS0eBbZhAc0'
BOT_TOKEN_VIP = '7557496462:AAG5pa4rkbikdBYiNAEr9tuNCSDRp53yv54'
CHAT_ID = '5828174289'  # Reemplaza con el chat ID correcto

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

@app.route('/fletes-mudanzas')
def fletes_mudanzas():
    return render_template('fletes_mudanzas.html')

@app.route('/apoyo-hoteles')
def apoyo_hoteles():
    return render_template('apoyo_hoteles.html')


@app.route('/alta-gama')
def alta_gama():
    return render_template('alta_gama.html')

# Ruta para la ventana emergente
@app.route('/')
def ventana_emergente():
    return render_template('emergente.html')

# Ruta para la ventana principal
@app.route('/principal')
def principal():
    return render_template('principal.html')

# Ruta para el formulario de Taxi
@app.route('/taxi-service')
def taxi_service():
    return render_template('taxi.html')

# Procesar formulario de Taxi
@app.route('/solicitar-taxi', methods=['POST'])
def solicitar_taxi():
    try:
        nombre = request.form.get('nombre')
        telefono = request.form.get('telefono')
        lugar_recogida = request.form.get('lugar_recogida')
        destino = request.form.get('destino')
        pasajeros = request.form.get('pasajeros')

        mensaje = (
            "*Solicitud de Taxi*\n\n"
            f"👤 Nombre: {nombre}\n"
            f"📞 Teléfono: {telefono}\n"
            f"📍 Lugar de Recogida: {lugar_recogida}\n"
            f"🎯 Destino: {destino}\n"
            f"👥 Pasajeros: {pasajeros}"
        )

        enviar_mensaje(mensaje, BOT_TOKEN_TAXI)
        return render_template('success.html', mensaje="¡Gracias! Su solicitud de taxi ha sido enviada.")
    except Exception as e:
        app.logger.error(f"Error en /solicitar-taxi: {e}")
        return "Error al procesar la solicitud de taxi.", 500

# Ruta para el formulario de Turismo
@app.route('/turismo')
def turismo():
    return render_template('turismo.html')

# Procesar formulario de Turismo
@app.route('/solicitar-turismo', methods=['POST'])
def solicitar_turismo():
    try:
        nombre = request.form.get('nombre')
        telefono = request.form.get('telefono')
        origen = request.form.get('origen')
        destino = request.form.get('destino')
        fecha = request.form.get('fecha')

        mensaje = (
            "*Solicitud de Turismo Local y Nacional*\n\n"
            f"👤 Nombre: {nombre}\n"
            f"📞 Teléfono: {telefono}\n"
            f"📍 Origen: {origen}\n"
            f"🎯 Destino: {destino}\n"
            f"📅 Fecha: {fecha}"
        )

        enviar_mensaje(mensaje, BOT_TOKEN_VIP)
        return render_template('success.html', mensaje="¡Gracias! Su solicitud de turismo ha sido enviada.")
    except Exception as e:
        app.logger.error(f"Error en /solicitar-turismo: {e}")
        return "Error al procesar la solicitud de turismo.", 500

# Ruta para el formulario de Alta Gama
@app.route('/alta-gama')
def alta_gama():
    return render_template('formulario_alta_gama.html')

# Procesar formulario de Alta Gama
@app.route('/solicitar-alta-gama', methods=['POST'])
def solicitar_alta_gama():
    try:
        nombre = request.form.get('nombre')
        telefono = request.form.get('telefono')
        tipo_vehiculo = request.form.get('tipo_vehiculo')
        fecha = request.form.get('fecha')
        hora = request.form.get('hora')
        detalles = request.form.get('detalles')

        mensaje = (
            "*Solicitud de Alta Gama*\n\n"
            f"👤 Nombre: {nombre}\n"
            f"📞 Teléfono: {telefono}\n"
            f"🚘 Tipo de Vehículo: {tipo_vehiculo}\n"
            f"📅 Fecha: {fecha}\n"
            f"⏰ Hora: {hora}\n"
            f"📋 Detalles Adicionales: {detalles}"
        )

        # Enviar mensaje a Telegram
        enviar_mensaje(mensaje, BOT_TOKEN_VIP)

        # Mostrar página de éxito con ventana emergente
        return render_template('success.html', mensaje="¡Gracias! Su solicitud de Alta Gama ha sido enviada.")
    except Exception as e:
        app.logger.error(f"Error en /solicitar-alta-gama: {e}")
        return "Error al procesar la solicitud de Alta Gama.", 500


if __name__ == '__main__':
    app.run(debug=True)
