from flask import Flask, render_template, request
import telegram
import asyncio
import logging

app = Flask(__name__)

# Configuración de bots y chat ID
BOT_TOKEN_TAXI = '8146583492:AAFP-9CTNvmNR13aFxvJB6Q1WS0eBbZhAc0'
BOT_TOKEN_VIP = '7557496462:AAG5pa4rkbikdBYiNAEr9tuNCSDRp53yv54'
CHAT_ID = '5828174289'

bot_taxi = telegram.Bot(token=BOT_TOKEN_TAXI)
bot_vip = telegram.Bot(token=BOT_TOKEN_VIP)

logging.basicConfig(level=logging.DEBUG)

async def enviar_mensaje_async(mensaje, bot):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=mensaje, parse_mode='Markdown')
    except Exception as e:
        logging.error(f"Error al enviar mensaje: {e}")

def enviar_mensaje(mensaje, bot):
    asyncio.run(enviar_mensaje_async(mensaje, bot))

@app.route('/')
def principal():
    return render_template('principal.html')

# Botón "Taxi"
@app.route('/taxi-service')
def taxi_service():
    return render_template('taxi.html')

@app.route('/solicitar-taxi', methods=['POST'])
def solicitar_taxi():
    try:
        nombre = request.form['nombre']
        telefono = request.form['telefono']
        lugar_recogida = request.form['lugar_recogida']
        destino = request.form['destino']
        pasajeros = request.form['pasajeros']

        mensaje = (
            f"*Solicitud de Taxi*\n\n"
            f"Nombre: {nombre}\n"
            f"Teléfono: {telefono}\n"
            f"Lugar de recogida: {lugar_recogida}\n"
            f"Destino: {destino}\n"
            f"Número de pasajeros: {pasajeros}"
        )
        enviar_mensaje(mensaje, bot_taxi)
        return render_template('gracias.html', mensaje="¡Gracias! Su solicitud de taxi ha sido enviada.")
    except Exception as e:
        logging.error(f"Error en /solicitar-taxi: {e}")
        return "Error al procesar la solicitud de taxi.", 500

# Botón "Turismo Local y Nacional"
@app.route('/turismo')
def turismo():
    return render_template('turismo.html')

@app.route('/solicitar-turismo', methods=['POST'])
def solicitar_turismo():
    try:
        nombre = request.form['nombre']
        telefono = request.form['telefono']
        destino = request.form['destino']
        fecha = request.form['fecha']
        personas = request.form['personas']

        mensaje = (
            f"*Solicitud de Turismo*\n\n"
            f"Nombre: {nombre}\n"
            f"Teléfono: {telefono}\n"
            f"Destino: {destino}\n"
            f"Fecha: {fecha}\n"
            f"Número de personas: {personas}"
        )
        enviar_mensaje(mensaje, bot_vip)
        return render_template('gracias.html', mensaje="¡Gracias! Su solicitud de turismo ha sido enviada.")
    except Exception as e:
        logging.error(f"Error en /solicitar-turismo: {e}")
        return "Error al procesar la solicitud de turismo.", 500

# Botón "Fletes y Mudanzas"
@app.route('/fletes-mudanzas')
def fletes_mudanzas():
    return render_template('fletes.html')

@app.route('/solicitar-flete', methods=['POST'])
def solicitar_flete():
    try:
        nombre = request.form['nombre']
        telefono = request.form['telefono']
        origen = request.form['origen']
        destino = request.form['destino']
        descripcion = request.form['descripcion']

        mensaje = (
            f"*Solicitud de Fletes y Mudanzas*\n\n"
            f"Nombre: {nombre}\n"
            f"Teléfono: {telefono}\n"
            f"Origen: {origen}\n"
            f"Destino: {destino}\n"
            f"Descripción: {descripcion}"
        )
        enviar_mensaje(mensaje, bot_vip)
        return render_template('gracias.html', mensaje="¡Gracias! Su solicitud de flete ha sido enviada.")
    except Exception as e:
        logging.error(f"Error en /solicitar-flete: {e}")
        return "Error al procesar la solicitud de flete.", 500

# Botón "Apoyo Hoteles"
@app.route('/apoyo-hoteles')
def apoyo_hoteles():
    return render_template('apoyo_hoteles.html')

@app.route('/verificar-codigo', methods=['POST'])
def verificar_codigo():
    try:
        codigo = request.form['codigo']
        codigos_validos = ['515', '122', '155']
        if codigo in codigos_validos:
            return render_template('opciones_hoteles.html')
        else:
            return render_template('error.html', mensaje="Código inválido. Por favor, intente de nuevo.")
    except Exception as e:
        logging.error(f"Error en /verificar-codigo: {e}")
        return "Error al procesar el código.", 500

if __name__ == '__main__':
    app.run(debug=True)
