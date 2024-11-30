from flask import Flask, render_template

app = Flask(__name__)

# Ruta para la página principal
@app.route('/')
def principal():
    return render_template('principal.html')

# Ruta para el servicio de Taxi
@app.route('/taxi-service')
def taxi_service():
    return render_template('taxi.html')  # Asegúrate de que el archivo taxi.html exista

# Ruta para Turismo Local y Nacional
@app.route('/turismo')
def turismo():
    return render_template('turismo.html')  # Asegúrate de que el archivo turismo.html exista

# Ruta para Alta Gama
@app.route('/alta-gama')
def alta_gama():
    return render_template('alta_gama.html')  # Asegúrate de que el archivo alta_gama.html exista

# Ruta para Fletes y Mudanzas
@app.route('/fletes-mudanzas')
def fletes_mudanzas():
    return render_template('fletes_mudanzas.html')  # Asegúrate de que el archivo fletes_mudanzas.html exista

# Ruta para Apoyo Hoteles
@app.route('/apoyo-hoteles')
def apoyo_hoteles():
    return render_template('apoyo_hoteles.html')  # Asegúrate de que el archivo apoyo_hoteles.html exista

if __name__ == '__main__':
    app.run(debug=True)
