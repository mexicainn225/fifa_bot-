import os
import database
from flask import Flask, render_template, request
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, Update

app = Flask(__name__, template_folder='templates', static_folder='static')
TOKEN = os.environ.get("TOKEN")
TON_ID_ADMIN = 5724620019
URL_WEBAPP = "https://fifa-bot-rnbr.onrender.com"

# Initialisation du bot Telegram
bot = Bot(token=TOKEN) if TOKEN else None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == "POST":
        json_data = request.get_json(force=True)
        if json_data and bot:
            try:
                update = Update.de_json(json_data, bot)
                
                if update.message and update.message.text:
                    user_id = update.effective_user.id
                    message_text = update.message.text
                    
                    if message_text.startswith('/start'):
                        if database.est_valide(user_id):
                            keyboard = [[InlineKeyboardButton("🚀 Lancer l'Application FIFA", web_app=WebAppInfo(url=URL_WEBAPP))]]
                            bot.send_message(
                                chat_id=user_id,
                                text="Re-bonjour champion ! Voici ton accès direct :",
                                reply_markup=InlineKeyboardMarkup(keyboard)
                            )
                        else:
                            message = (
                                "Bienvenue sur le bot FIFA VIP ⚽\n\n"
                                "Pour débloquer tes accès aux pronostics, suis ces étapes :\n\n"
                                "1️⃣ Inscris-toi sur Melbet ici : https://lkbb.cc/78634e\n"
                                "2️⃣ Utilise le code promo : COK225\n"
                                "3️⃣ Effectue une recharge sur ton compte.\n"
                                "4️⃣ Envoie ton ID Melbet ici pour validation."
                            )
                            bot.send_message(chat_id=user_id, text=message)
                            
                    elif message_text.startswith('/valider'):
                        if user_id == TON_ID_ADMIN:
                            parts = message_text.split()
                            if len(parts) > 1:
                                user_id_a_valider = int(parts[1])
                                database.valider_utilisateur(user_id_a_valider)
                                keyboard = [[InlineKeyboardButton("🚀 Lancer l'Application FIFA", web_app=WebAppInfo(url=URL_WEBAPP))]]
                                bot.send_message(
                                    chat_id=user_id_a_valider,
                                    text="✅ Félicitations ! Ton ID a été validé. Tu peux maintenant accéder aux pronos FIFA.",
                                    reply_markup=InlineKeyboardMarkup(keyboard)
                                )
                                bot.send_message(chat_id=user_id, text=f"Utilisateur {user_id_a_valider} validé avec succès !")
                    else:
                        # Enregistrement de l'ID Melbet
                        database.ajouter_utilisateur(user_id, message_text)
                        bot.send_message(chat_id=user_id, text="ID Melbet reçu ! J'ai transmis ta demande à l'admin. Attends la validation. ✅")
                        bot.send_message(
                            chat_id=TON_ID_ADMIN, 
                            text=f"🚨 Nouvelle demande FIFA :\nUser ID: {user_id}\nID Melbet: {message_text}\n\nTape: /valider {user_id}"
                        )
            except Exception as e:
                print(f"Erreur dans le webhook : {e}")
                
    return "OK", 200

def set_webhook():
    if TOKEN and bot:
        webhook_url = f"{URL_WEBAPP}/webhook"
        # Utilisation de requests ou de l'appel synchrone natif du bot si dispo, sinon on laisse Telegram gérer via le setWebhook déjà fait
        print(f"Application prête à recevoir les webhooks sur : {webhook_url}")

if __name__ == '__main__':
    set_webhook()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
else:
    set_webhook()
