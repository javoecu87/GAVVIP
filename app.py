from flask import Flask, render_template, request
import telegram
import logging

app = Flask(__name__)

# Configura el bot de Telegram
BOT_TOKEN = '7557496462:AAG5pa4rkbikdBYiNAEr9tuNCSDRp53yv54'
CHAT_ID = '5828174289'

# Configuración de logging para asegurar la salida en consola
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[logging.StreamHandler()]
)

# Función para enviar el mensaje sin usar asyncio
def enviar_mensaje(mensaje):
    bot = telegram.Bot(token=BOT_TOKEN)
    try:
        bot.send_message(chat_id=CHAT_ID, text=mensaje, parse_mode='Markdown')
        app.logger.debug("Mensaje enviado a Telegram con éxito")
    except Exception as e:
        app.logger.error(f"Error al enviar mensaje a Telegram: {e}")

# Ruta para la ventana principal
@app.route('/')
def principal():
    app.logger.debug("Cargando la ventana principal.")
    return render_template('principal.html')

# Ruta para el servicio de Taxi
@app.route('/taxi-service')
def taxi_service():
    app.logger.debug("Cargando la ventana de servicio de Taxi.")
    return render_template('taxi.html')

# Ruta para el formulario de Quito Tour VIP
@app.route('/reservar-formulario')
def reservar_formulario():
    app.logger.debug("Cargando el formulario de Quito Tour VIP.")
    return render_template('index.html')

# Ruta para procesar la solicitud de taxi
@app.route('/solicitar-taxi', methods=['POST'])
def solicitar_taxi():
    try:
        nombre = request.form['nombre']
        telefono = request.form['telefono']
        ubicacion = request.form['ubicacion']
        destino = request.form.get('destino', 'No especificado')
        observaciones = request.form.get('observaciones', 'No especificadas')

        mensaje = (
            "🚖 *Solicitud de Taxi*\n\n"
            f"👤 *Nombre:* {nombre}\n"
            f"📞 *Teléfono:* {telefono}\n"
            f"📍 *Ubicación:* {ubicacion}\n"
            f"➡️ *Destino:* {destino}\n"
            f"📝 *Observaciones:* {observaciones}"
        )

        enviar_mensaje(mensaje)
        app.logger.debug("Redirigiendo a página de agradecimiento.")
        return render_template('gracias.html', mensaje="¡Gracias! Su solicitud de taxi ha sido enviada.")
    except Exception as e:
        app.logger.error(f"Error en /solicitar-taxi: {e}")
        return "Error al procesar la solicitud de taxi.", 500

# Ruta para procesar el formulario de reserva de Quito Tour VIP
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
            "🚌 *Reserva de Quito Tour VIP*\n\n"
            f"👤 *Nombre:* {nombre}\n"
            f"📞 *Teléfono:* {telefono}\n"
            f"📍 *Origen:* {origen}\n"
            f"➡️ *Destino:* {destino}\n"
            f"📅 *Fecha:* {fecha}\n"
            f"⏰ *Hora:* {hora}\n"
            f"👥 *Personas:* {personas}"
        )

        enviar_mensaje(mensaje)
        app.logger.debug("Redirigiendo a página de agradecimiento.")
        return render_template('gracias.html', mensaje="¡Gracias! Su reservación está confirmada.")
    except Exception as e:
        app.logger.error(f"Error en /reservar: {e}")
        return "Error al procesar la reserva.", 500

if __name__ == '__main__':
    app.run(debug=True)
