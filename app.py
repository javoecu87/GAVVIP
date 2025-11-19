from flask import Flask, render_template, request, send_from_directory
import telegram
import asyncio
import logging

app = Flask(__name__)

# Tokens de los bots para los formularios
BOT_TOKEN_TAXI = '8146583492:AAG5pa4rkbikdBYiNAEr9tuNCSDRp53yv54'
BOT_TOKEN_VIP = '7557496462:AAG5pa4rkbikdBYiNAEr9tuNCSDRp53yv54'
BOT_TOKEN_TURISMO = '8590651604:AAFXhSpGmtjNy89FBQGQ3xvXVB0t5cakZ8g'

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

# ✅ Nueva función para servir archivos en static/images/
@app.route('/static/images/<path:filename>')
def serve_images(filename):
    return send_from_directory('static/images', filename)

@app.route('/socio')
def socio():
    return render_template('socio.html')


@app.route('/registro_socio')
def registro_socio():
    return render_template('registro_socio.html')


@app.route('/verificar_socio')
def verificar_socio():
    return render_template('verificar_socio.html')



# Rutas de la ventana principal y sus botones
@app.route('/')
def ventana_emergente():
    return render_template('emergente.html')

@app.route('/principal')
def principal():
    return render_template('principal.html')

@app.route('/taxi-service')
def taxi_service():
    return render_template('taxi.html')

@app.route('/turismo-subventana')
def turismo_subventana():
    return render_template('turismo_subventana.html')

@app.route('/turismo-ecuador')
def turismo_ecuador():
    return render_template('turismo-ecuador.html')

@app.route('/turismo')
def turismo():
    return render_template('turismo.html')


@app.route('/ecuador-420')
def ecuador_420():
    return render_template('ecuador-420.html')

@app.route('/fletes-mudanzas')
def fletes_mudanzas():
    return render_template('fletes_mudanzas.html')

@app.route('/alta-gama')
def alta_gama():
    vehiculos = ['SUV', 'Van', 'Sedan']
    return render_template('alta_gama.html', vehiculos=vehiculos)

@app.route('/alta-gama/formulario')
def formulario_alta_gama():
    # Tomamos el vehículo desde la URL ?vehiculo=SUV
    vehiculo = request.args.get('vehiculo', 'No especificado')
    return render_template('formulario_alta_gama.html', vehiculo=vehiculo)


@app.route('/apoyo-hoteles')
def apoyo_hoteles():
    return render_template('apoyo_hoteles.html')

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

        # Enviar mensaje usando el nuevo bot de Turismo
        enviar_mensaje(mensaje, BOT_TOKEN_TURISMO)

        return render_template(
            'success.html',
            mensaje="¡Gracias! Tu solicitud de Turismo ha sido enviada."
        )
    except Exception as e:
        app.logger.error(f"Error en /solicitar-turismo: {e}")
        return "Error al procesar la solicitud de Turismo.", 500


@app.route('/enviar_taxi', methods=['POST'])
def enviar_taxi():
    try:
        nombre = request.form.get('nombre')
        telefono = request.form.get('telefono')
        origen = request.form.get('origen')
        destino = request.form.get('destino')
        pasajeros = request.form.get('pasajeros')
        metodo_pago = request.form.get('metodo_pago')
        comentarios = request.form.get('comentarios')
        tipo_servicio = request.form.get('tipo_servicio')

        mensaje = (
            "*🚕 SOLICITUD DE TAXI*\n\n"
            f"👤 Nombre: {nombre}\n"
            f"📞 Teléfono: {telefono}\n"
            f"📍 Origen: {origen}\n"
            f"🎯 Destino: {destino}\n"
            f"👥 Pasajeros: {pasajeros}\n"
            f"💳 Pago: {metodo_pago}\n"
            f"🚗 Servicio: {tipo_servicio}\n"
            f"📝 Comentarios: {comentarios if comentarios else 'Ninguno'}"
        )

        # Enviar mensaje al bot TAXI
        enviar_mensaje(mensaje, BOT_TOKEN_TAXI)

        return render_template(
            'success.html',
            mensaje="¡Gracias! Tu solicitud de Taxi ha sido enviada con éxito."
        )
    except Exception as e:
        app.logger.error(f"Error en /enviar_taxi: {e}")
        return "Error al procesar la solicitud de taxi.", 500


@app.route('/conductor')
def conductor():
    return render_template('conductor.html')


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

@app.route('/solicitar-ecuador-420', methods=['POST'])
def solicitar_ecuador_420():
    try:
        nombre = request.form.get('nombre')
        telefono = request.form.get('telefono')
        ciudad = request.form.get('ciudad')
        fecha = request.form.get('fecha')
        detalles = request.form.get('detalles')

        mensaje = (
            "*Solicitud Ecuador 420*\n\n"
            f"👤 Nombre: {nombre}\n"
            f"📞 Teléfono: {telefono}\n"
            f"📍 Ciudad / Provincia: {ciudad}\n"
            f"📅 Fecha tentativa: {fecha}\n"
            f"📋 Detalles: {detalles}"
        )

        # Mismo bot que Turismo
        enviar_mensaje(mensaje, BOT_TOKEN_TURISMO)

        return render_template(
            'success.html',
            mensaje="¡Gracias! Tu solicitud Ecuador 420 ha sido enviada."
        )
    except Exception as e:
        app.logger.error(f"Error en /solicitar-ecuador-420: {e}")
        return "Error al procesar la solicitud Ecuador 420.", 500


@app.route('/procesar_solicitud_alta_gama', methods=['POST'])
def procesar_solicitud_alta_gama():
    try:
        nombre = request.form.get('nombre')
        telefono = request.form.get('telefono')
        vehiculo = request.form.get('tipo_vehiculo')
        fecha = request.form.get('fecha')
        hora = request.form.get('hora')
        detalles = request.form.get('detalles')

        mensaje = (
            "*Solicitud de Alta Gama*\n\n"
            f"👤 Nombre: {nombre}\n"
            f"📞 Teléfono: {telefono}\n"
            f"🚗 Vehículo: {vehiculo}\n"
            f"📅 Fecha: {fecha}\n"
            f"⏰ Hora: {hora}\n"
            f"📋 Detalles: {detalles}"
        )

        # Usamos el bot VIP para este servicio
        enviar_mensaje(mensaje, BOT_TOKEN_VIP)

        return render_template(
            'success.html',
            mensaje="¡Gracias! Tu solicitud de Alta Gama ha sido enviada."
        )
    except Exception as e:
        app.logger.error(f"Error en /procesar_solicitud_alta_gama: {e}")
        return "Error al procesar la solicitud de Alta Gama.", 500


if __name__ == '__main__':
    app.run(debug=True)
