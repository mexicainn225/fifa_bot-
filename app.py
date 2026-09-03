import os
import asyncio
import database # Importe ton fichier database.py
from flask import Flask, render_template
from threading import Thread
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

app = Flask(__name__, template_folder='templates', static_folder='static')
TOKEN = os.environ.get("TOKEN")
TON_ID_ADMIN = 5724620019 # Ton ID Admin Telegram

# URL exacte de ton service sur Render
URL_WEBAPP = "https://fifa-bot-rnbr.onrender.com"

@app.route('/')
def home():
    return render_template('index.html')

async def start(update, context):
    user_id = update.effective_user.id
    
    # Si l'utilisateur est déjà validé dans Supabase, on lui donne l'accès direct
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

async def handle_message(update, context):
    user_id = update.effective_user.id
    message_text = update.message.text
    
    # Enregistre l'ID Melbet et met le statut en 'pending' dans Supabase
    database.ajouter_utilisateur(user_id, message_text)
    
    await update.message.reply_text("ID Melbet reçu ! J'ai transmis ta demande à l'admin. Attends la validation. ✅")
    
    # Alerte l'admin avec les informations pour valider
    await context.bot.send_message(
        chat_id=TON_ID_ADMIN, 
        text=f"🚨 Nouvelle demande FIFA :\nUser ID: {user_id}\nID Melbet: {message_text}\n\nTape: /valider {user_id}"
    )

async def valider(update, context):
    # Sécurité : seul l'admin peut exécuter cette commande
    if update.effective_user.id != TON_ID_ADMIN:
        return
    
    if context.args:
        user_id_a_valider = int(context.args[0])
        database.valider_utilisateur(user_id_a_valider)
        
        # Envoi du bouton WebApp à l'abonné validé
        keyboard = [[InlineKeyboardButton("🚀 Lancer l'Application FIFA", web_app=WebAppInfo(url=URL_WEBAPP))]]
        await context.bot.send_message(
            chat_id=user_id_a_valider,
            text="✅ Félicitations ! Ton ID a été validé. Tu peux maintenant accéder aux pronos FIFA.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        await update.message.reply_text(f"Utilisateur {user_id_a_valider} validé avec succès !")

async def main_bot():
    bot_app = ApplicationBuilder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("valider", valider))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    await bot_app.initialize()
    await bot_app.start()
    await bot_app.updater.start_polling(drop_pending_updates=True)
    
    # Maintient le bot actif dans son thread
    stop_event = asyncio.Event()
    await stop_event.wait()

def run_bot():
    try:
        print("Démarrage du thread du bot Telegram avec asyncio.run...")
        asyncio.run(main_bot())
    except Exception as e:
        print(f"❌ Erreur critique dans le bot Telegram : {e}")

# Lancement automatique du bot en arrière-plan dès que Gunicorn charge l'application sur Render
if TOKEN:
    bot_thread = Thread(target=run_bot, daemon=True)
    bot_thread.start()
    print("Thread du bot initialisé.")
else:
    print("❌ ERREUR : Aucun TOKEN trouvé dans les variables d'environnement !")
