from flask import Flask, render_template

app = Flask(__name__)

# Ruta para la ventana emergente
@app.route('/')
def emergente():
    return render_template('emergente.html')

# Ruta para la página principal
@app.route('/principal')
def principal():
    return render_template('principal.html')

# Ruta para el servicio de Taxi
@app.route('/taxi-service')
def taxi_service():
    return render_template('taxi.html')

# Ruta para Turismo Local y Nacional
@app.route('/turismo')
def turismo():
    return render_template('turismo.html')

# Ruta para Alta Gama
@app.route('/alta-gama')
def alta_gama():
    return render_template('alta_gama.html')

# Ruta para Fletes y Mudanzas
@app.route('/fletes-mudanzas')
def fletes_mudanzas():
    return render_template('fletes_mudanzas.html')

# Ruta para Apoyo Hoteles
@app.route('/apoyo-hoteles')
def apoyo_hoteles():
    return render_template('apoyo_hoteles.html')

if __name__ == '__main__':
    app.run(debug=True)
