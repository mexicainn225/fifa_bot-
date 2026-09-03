import os
import database
from flask import Flask, request, render_template
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
import asyncio

app = Flask(__name__, template_folder='templates', static_folder='static')
TOKEN = os.environ.get("TOKEN")
TON_ID_ADMIN = 5724620019
URL_WEBAPP = "https://fifa-bot-rnbr.onrender.com"

# Initialisation propre de l'application Telegram
telegram_app = ApplicationBuilder().token(TOKEN).concurrent_updates(True).build()

async def start(update: Update, context):
    user_id = update.effective_user.id
    if database.est_valide(user_id):
        keyboard = [[InlineKeyboardButton("🚀 Lancer l'Application FIFA", web_app=WebAppInfo(url=URL_WEBAPP))]]
        await update.message.reply_text("Re-bonjour champion ! Voici ton accès direct :", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        message = (
            "Bienvenue sur le bot FIFA VIP ⚽\n\n"
            "Pour débloquer tes accès aux pronostics, suis ces étapes :\n\n"
            "1️⃣ Inscris-toi sur Melbet ici : https://lkbb.cc/78634e\n"
            "2️⃣ Utilise le code promo : COK225\n"
            "3️⃣ Effectue une recharge sur ton compte.\n"
            "4️⃣ Envoie ton ID Melbet ici pour validation."
        )
        await update.message.reply_text(message)

async def handle_message(update: Update, context):
    user_id = update.effective_user.id
    message_text = update.message.text
    
    database.ajouter_utilisateur(user_id, message_text)
    await update.message.reply_text("ID Melbet reçu ! J'ai transmis ta demande à l'admin. Attends la validation. ✅")
    
    await context.bot.send_message(
        chat_id=TON_ID_ADMIN, 
        text=f"🚨 Nouvelle demande FIFA :\nUser ID: {user_id}\nID Melbet: {message_text}\n\nTape: /valider {user_id}"
    )

async def valider(update: Update, context):
    if update.effective_user.id != TON_ID_ADMIN:
        return
    
    if context.args:
        user_id_a_valider = int(context.args[0])
        database.valider_utilisateur(user_id_a_valider)
        
        keyboard = [[InlineKeyboardButton("🚀 Lancer l'Application FIFA", web_app=WebAppInfo(url=URL_WEBAPP))]]
        await context.bot.send_message(
            chat_id=user_id_a_valider,
            text="✅ Félicitations ! Ton ID a été validé. Ton accès est ouvert.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        await update.message.reply_text(f"Utilisateur {user_id_a_valider} validé avec succès !")

# Enregistrement des commandes
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("valider", valider))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Variable pour s'assurer que l'application telegram est initialisée une seule fois
_initialized = False

async def initialize_telegram():
    global _initialized
    if not _initialized:
        await telegram_app.initialize()
        _initialized = True

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/set_webhook')
def set_webhook_manual():
    bot = Bot(TOKEN)
    webhook_url = f"{URL_WEBAPP}/{TOKEN}"
    
    async def reg():
        await bot.set_webhook(url=webhook_url)
    
    asyncio.run(reg())
    return f"Webhook configuré avec succès sur : {webhook_url}", 200

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    json_data = request.get_json(force=True)
    update = Update.de_json(json_data, telegram_app.bot)
    
    # Utilisation d'une boucle locale propre pour éviter le "Event loop is closed"
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    async def process():
        await initialize_telegram()
        await telegram_app.process_update(update)

    try:
        loop.run_until_complete(process())
    finally:
        loop.close()
        
    return 'ok', 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
