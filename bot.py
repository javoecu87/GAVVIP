from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Función para manejar el comando /start con un botón para abrir la mini app dentro de Telegram
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Crear el botón de Web App para abrir la mini aplicación dentro de Telegram
    keyboard = [
        [InlineKeyboardButton("Abrir Mini App en Telegram", web_app=WebAppInfo(url="https://gavvip.onrender.com"))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Enviar el mensaje con el botón de Web App
    await update.message.reply_text(
        "¡Hola! Haz clic en el botón para abrir la mini aplicación dentro de Telegram:",
        reply_markup=reply_markup
    )

# Token del bot
TOKEN = '7557496462:AAG5pa4rkbikdBYiNAEr9tuNCSDRp53yv54'

def main():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.run_polling()

if __name__ == '__main__':
    main()
