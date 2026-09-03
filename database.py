import os
from supabase import create_client, Client

# Récupération des clés depuis les variables d'environnement (Render)
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(url, key)

def ajouter_utilisateur(user_id: int, id_melbet: str):
    """Enregistre un nouvel utilisateur ou met à jour son ID Melbet avec le statut 'pending'"""
    data = {
        "user_id": user_id,
        "id_1win": str(id_melbet),  # Utilise le nom de ta colonne dans Supabase
        "statut": "pending"
    }
    # upsert permet de mettre à jour si l'utilisateur existe déjà, sinon de l'insérer
    supabase.table("utilisateurs").upsert(data).execute()

def valider_utilisateur(user_id: int):
    """Met le statut de l'utilisateur à 'valide'"""
    supabase.table("utilisateurs").update({"statut": "valide"}).eq("user_id", user_id).execute()

def est_valide(user_id: int) -> bool:
    """Vérifie si l'utilisateur a le statut 'valide' dans la base de données"""
    response = supabase.table("utilisateurs").select("statut").eq("user_id", user_id).execute()
    
    if response.data:
        # On regarde si le premier résultat a le statut 'valide'
        return response.data[0].get("statut") == "valide"
    return False
