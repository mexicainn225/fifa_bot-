import os
from supabase import create_client

# Récupère les clés depuis les variables d'environnement sur Render
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

def ajouter_utilisateur(user_id, id_melbet):
    # Insère ou met à jour l'utilisateur dans la table "users"
    try:
        supabase.table("users").upsert({
            "user_id": user_id, 
            "id_1win": id_melbet, # On garde la colonne "id_1win" en base pour ne pas casser la table existante, mais on y stocke l'ID Melbet
            "status": "pending"
        }).execute()
    except Exception as e:
        print(f"Erreur Supabase (ajouter_utilisateur) : {e}")

def valider_utilisateur(user_id):
    # Change le statut en 'active'
    try:
        supabase.table("users").update({"status": "active"}).eq("user_id", user_id).execute()
    except Exception as e:
        print(f"Erreur Supabase (valider_utilisateur) : {e}")

def est_valide(user_id):
    # Vérifie si le statut est 'active' avec une sécurité anti-crash réseau
    try:
        response = supabase.table("users").select("status").eq("user_id", user_id).execute()
        data = response.data
        return len(data) > 0 and data[0].get('status') == 'active'
    except Exception as e:
        print(f"Erreur Supabase (est_valide - ignorée pour éviter le crash) : {e}")
        return False
