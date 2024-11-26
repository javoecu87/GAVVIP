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

@app.route('/alta-gama')
def alta_gama():
    return render_template('alta_gama.html')

@app.route('/formulario-alta-gama', methods=['POST'])
def formulario_alta_gama():
    vehiculo = request.form.get('vehiculo')
    return render_template('formulario_alta_gama.html', vehiculo=vehiculo)

@app.route('/procesar-alta-gama', methods=['POST'])
def procesar_alta_gama():
    try:
        vehiculo = request.form.get('vehiculo')
        nombre = request.form.get('nombre')
        recogida = request.form.get('recogida')
        tiempo = request.form.get('tiempo')

        mensaje = (
            f"*Solicitud de Alta Gama*\n\n"
            f"Vehículo: {vehiculo}\n"
            f"Nombre: {nombre}\n"
            f"Lugar de recogida: {recogida}\n"
            f"Tiempo estimado: {tiempo}"
        )

        enviar_mensaje(mensaje, bot_vip)
        return render_template('gracias.html', mensaje="¡Un placer servirte! Tu vehículo llegará a tiempo.")
    except Exception as e:
        logging.error(f"Error procesando Alta Gama: {e}")
        return "Error al procesar la solicitud.", 500

if __name__ == '__main__':
    app.run(debug=True)
