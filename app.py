@app.route('/reservar', methods=['POST'])
def reservar():
    # Recoge los datos del formulario
    nombre = request.form['nombre']
    telefono = request.form['telefono']
    origen = request.form['origen']
    destino = request.form['destino']
    fecha = request.form['fecha']
    hora = request.form['hora']
    personas = request.form['personas']

    # Crea el mensaje de reserva
    mensaje = (f"Reserva recibida:\n"
               f"Nombre: {nombre}\n"
               f"Teléfono: {telefono}\n"
               f"Origen: {origen}\n"
               f"Destino: {destino}\n"
               f"Fecha: {fecha}\n"
               f"Hora: {hora}\n"
               f"Personas: {personas}")

    # Define una función para enviar el mensaje de forma asíncrona
    async def enviar_mensaje():
        await bot.send_message(chat_id=CHAT_ID, text=mensaje)

    # Ejecuta la función asincrónica
    asyncio.run(enviar_mensaje())

    # Redirige al usuario a la página principal después de enviar la reserva
    return redirect(url_for('home'))
