import os
from supabase import create_client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

def ajouter_utilisateur(user_id, id_melbet):
    try:
        supabase.table("utilisateurs").upsert({
            "user_id": int(user_id), 
            "id_1win": str(id_melbet),
            "statut": "pending"
        }).execute()
    except Exception as e:
        print(f"Erreur Supabase (ajouter_utilisateur) : {e}")

def valider_utilisateur(user_id):
    try:
        supabase.table("utilisateurs").update({"statut": "active"}).eq("user_id", int(user_id)).execute()
    except Exception as e:
        print(f"Erreur Supabase (valider_utilisateur) : {e}")

def est_valide(user_id):
    try:
        response = supabase.table("utilisateurs").select("statut").eq("user_id", int(user_id)).execute()
        data = response.data
        return len(data) > 0 and data[0].get('statut') == 'active'
    except Exception as e:
        print(f"Erreur Supabase (est_valide) : {e}")
        return False
