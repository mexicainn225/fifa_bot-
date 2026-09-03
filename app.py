import os
import database
from flask import Flask, request
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, Update
from telegram import Bot, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
import asyncio

app = Flask(__name__)
TOKEN = os.environ.get("TOKEN")
TON_ID_ADMIN = 5724620019
URL_WEBAPP = "https://fifa-bot-rnbr.onrender.com"

# Initialisation de l'application Telegram pour les handlers
telegram_app = ApplicationBuilder().token(TOKEN).build()

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

@app.route('/')
def home():
    return "Bot FIFA en ligne et actif !"

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    """Route que Telegram appelle automatiquement à chaque message"""
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    asyncio.run(telegram_app.process_update(update))
    return 'ok', 200

if __name__ == '__main__':
    # Configuration automatique du webhook auprès de Telegram au démarrage
    bot_instance = Bot(TOKEN)
    webhook_url = f"{URL_WEBAPP}/{TOKEN}"
    asyncio.run(bot_instance.set_webhook(url=webhook_url))
    
    # Lancement du serveur web Flask sur le port de Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
