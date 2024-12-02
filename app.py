from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# Tokens de los bots
BOT_TOKEN_TAXI = '8146583492:AAG5pa4rkbikdBYiNAEr9tuNCSDRp53yv54'
BOT_TOKEN_VIP = '7557496462:AAG5pa4rkbikdBYiNAEr9tuNCSDRp53yv54'

# Función para enviar mensajes a Telegram
def send_message_to_telegram(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    response = requests.post(url, data=payload)
    return response.status_code

@app.route("/")
def main_page():
    return render_template("principal.html")

@app.route("/taxi-service", methods=["GET", "POST"])
def taxi_service():
    if request.method == "POST":
        name = request.form.get("name")
        pickup_location = request.form.get("pickup_location")
        message = f"Nuevo servicio de Taxi:\nNombre: {name}\nLugar de recogida: {pickup_location}"
        send_message_to_telegram(BOT_TOKEN_TAXI, "CHAT_ID_AQUI", message)
        return render_template("success.html", message="Solicitud enviada con éxito.")
    return render_template("taxi.html")

@app.route("/alta-gama", methods=["GET", "POST"])
def alta_gama():
    if request.method == "POST":
        name = request.form.get("name")
        location = request.form.get("location")
        time_needed = request.form.get("time_needed")
        message = f"Alta Gama:\nNombre: {name}\nLugar de recogida: {location}\nTiempo requerido: {time_needed}"
        send_message_to_telegram(BOT_TOKEN_VIP, "CHAT_ID_AQUI", message)
        return render_template("success.html", message="Solicitud enviada con éxito.")
    return render_template("alta_gama.html")

@app.route("/turismo", methods=["GET", "POST"])
def turismo():
    if request.method == "POST":
        name = request.form.get("name")
        destination = request.form.get("destination")
        date = request.form.get("date")
        message = f"Turismo:\nNombre: {name}\nDestino: {destination}\nFecha: {date}"
        send_message_to_telegram(BOT_TOKEN_VIP, "CHAT_ID_AQUI", message)
        return render_template("success.html", message="Solicitud enviada con éxito.")
    return render_template("turismo.html")

@app.route("/success")
def success():
    return render_template("success.html", message="Operación completada con éxito.")

if __name__ == "__main__":
    app.run(debug=True)
