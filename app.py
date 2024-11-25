from flask import Flask, render_template, request
import telegram
import asyncio
import logging

app = Flask(__name__)

# Configuración de los bots
BOT_TOKEN_VIP = '7557496462:AAG5pa4rkbikdBYiNAEr9tuNCSDRp53yv54'
CHAT_ID = '5828174289'

bot_vip = telegram.Bot(token=BOT_TOKEN_VIP)

# Función para enviar mensajes a Telegram
async def enviar_mensaje_async(mensaje):
    await bot_vip.send_message(chat_id=CHAT_ID, text=mensaje, parse_mode='Markdown')

def enviar_mensaje(mensaje):
    asyncio.run(enviar_mensaje_async(mensaje))

@app.route('/')
def principal():
    return render_template('principal.html')

@app.route('/alta-gama')
def alta_gama():
    return render_template('alta_gama.html')

@app.route('/formulario-alta-gama', methods=['POST'])
def formulario_alta_gama():
    vehiculo = request.form['vehiculo']
    return render_template('formulario_alta_gama.html', vehiculo=vehiculo)

@app.route('/procesar-alta-gama', methods=['POST'])
def procesar_alta_gama():
    try:
        vehiculo = request.form['vehiculo']
        nombre = request.form['nombre']
        recogida = request.form['recogida']
        tiempo = request.form['tiempo']

        mensaje = (
            "*Solicitud de Alta Gama*\n\n"
            f"Vehículo: {vehiculo}\n"
            f"Nombre: {nombre}\n"
            f"Lugar de recogida: {recogida}\n"
            f"Tiempo estimado: {tiempo}"
        )

        enviar_mensaje(mensaje)
        return render_template('gracias.html', mensaje="¡Un placer servirte! Tu vehículo llegará a tiempo.")
    except Exception as e:
        logging.error(f"Error en procesar-alta-gama: {e}")
        return "Error al procesar tu solicitud", 500

if __name__ == '__main__':
    app.run(debug=True)
