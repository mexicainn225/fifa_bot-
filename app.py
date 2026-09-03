import os
import requests
import database
from flask import Flask, request, render_template

app = Flask(__name__, template_folder='templates', static_folder='static')
TOKEN = os.environ.get("TOKEN")
TON_ID_ADMIN = 5724620019
URL_WEBAPP = "https://fifa-bot-rnbr.onrender.com"
TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"

def send_telegram_message(chat_id, text, reply_markup=None):
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    requests.post(url, json=payload)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/set_webhook')
def set_webhook_manual():
    webhook_url = f"{URL_WEBAPP}/{TOKEN}"
    url = f"{TELEGRAM_API}/setWebhook?url={webhook_url}"
    response = requests.get(url)
    return f"Webhook configuré : {response.text}", 200

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    data = request.get_json(force=True)
    
    if "message" in data:
        msg = data["message"]
        chat_id = msg["chat"]["id"]
        user_id = msg["from"]["id"]
        text = msg.get("text", "")
        
        # Commande /start
        if text.startswith("/start"):
            if database.est_valide(user_id):
                keyboard = {
                    "inline_keyboard": [[
                        {"text": "🚀 Lancer l'Application FIFA", "web_app": {"url": URL_WEBAPP}}
                    ]]
                }
                send_telegram_message(chat_id, "Re-bonjour champion ! Voici ton accès direct :", reply_markup=keyboard)
            else:
                message = (
                    "Bienvenue sur le bot FIFA VIP ⚽\n\n"
                    "Pour débloquer tes accès aux pronostics, suis ces étapes :\n\n"
                    "1️⃣ Inscris-toi sur Melbet ici : https://lkbb.cc/78634e\n"
                    "2️⃣ Utilise le code promo : COK225\n"
                    "3️⃣ Effectue une recharge sur ton compte.\n"
                    "4️⃣ Envoie ton ID Melbet ici pour validation."
                )
                send_telegram_message(chat_id, message)
                
        # Commande /valider (par l'admin)
        elif text.startswith("/valider") and user_id == TON_ID_ADMIN:
            parts = text.split()
            if len(parts) > 1:
                user_id_a_valider = int(parts[1])
                database.valider_utilisateur(user_id_a_valider)
                
                keyboard = {
                    "inline_keyboard": [[
                        {"text": "🚀 Lancer l'Application FIFA", "web_app": {"url": URL_WEBAPP}}
                    ]]
                }
                send_telegram_message(
                    user_id_a_valider,
                    "✅ Félicitations ! Ton ID a été validé. Ton accès est ouvert.",
                    reply_markup=keyboard
                )
                send_telegram_message(chat_id, f"Utilisateur {user_id_a_valider} validé avec succès !")
                
        # Réception de l'ID Melbet
        elif text and not text.startswith("/"):
            database.ajouter_utilisateur(user_id, text)
            send_telegram_message(chat_id, "ID Melbet reçu ! J'ai transmis ta demande à l'admin. Attends la validation. ✅")
            
            admin_text = f"🚨 Nouvelle demande FIFA :\nUser ID: {user_id}\nID Melbet: {text}\n\nTape: /valider {user_id}"
            send_telegram_message(TON_ID_ADMIN, admin_text)

    return 'ok', 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
