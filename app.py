import os
import asyncio
import database
from flask import Flask, render_template, request
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, Update

app = Flask(__name__, template_folder='templates', static_folder='static')
TOKEN = os.environ.get("TOKEN")
TON_ID_ADMIN = 5724620019
URL_WEBAPP = "https://fifa-bot-rnbr.onrender.com"

# Initialisation du bot Telegram global
bot = Bot(token=TOKEN) if TOKEN else None

@app.route('/')
def home():
    return render_template('index.html')

# Route webhook fixe et propre
@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == "POST":
        json_data = request.get_json(force=True)
        if json_data:
            update = Update.de_json(json_data, bot)
            asyncio.run(process_update(update))
    return "OK", 200

async def process_update(update):
    if not update.message:
        return
    
    user_id = update.effective_user.id
    message_text = update.message.text
    
    if message_text and message_text.startswith('/start'):
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
            
    elif message_text and message_text.startswith('/valider'):
        if user_id != TON_ID_ADMIN:
            return
        parts = message_text.split()
        if len(parts) > 1:
            user_id_a_valider = int(parts[1])
            database.valider_utilisateur(user_id_a_valider)
            keyboard = [[InlineKeyboardButton("🚀 Lancer l'Application FIFA", web_app=WebAppInfo(url=URL_WEBAPP))]]
            await bot.send_message(
                chat_id=user_id_a_valider,
                text="✅ Félicitations ! Ton ID a été validé. Tu peux maintenant accéder aux pronos FIFA.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            await update.message.reply_text(f"Utilisateur {user_id_a_valider} validé avec succès !")
    else:
        # Enregistrement de l'ID Melbet envoyé par l'utilisateur
        database.ajouter_utilisateur(user_id, message_text)
        await update.message.reply_text("ID Melbet reçu ! J'ai transmis ta demande à l'admin. Attends la validation. ✅")
        await bot.send_message(
            chat_id=TON_ID_ADMIN, 
            text=f"🚨 Nouvelle demande FIFA :\nUser ID: {user_id}\nID Melbet: {message_text}\n\nTape: /valider {user_id}"
        )

# Configuration automatique du webhook au démarrage pointant vers /webhook
def set_webhook():
    if TOKEN:
        webhook_url = f"{URL_WEBAPP}/webhook"
        asyncio.run(bot.set_webhook(url=webhook_url))
        print(f"Webhook configuré avec succès sur : {webhook_url}")

if __name__ == '__main__':
    set_webhook()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
else:
    set_webhook()
