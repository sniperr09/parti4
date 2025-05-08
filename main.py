import json
import os
from fastapi import FastAPI
import requests
from pydantic import BaseModel
from fastapi import Request

app = FastAPI()

class PersonnageWebhook(BaseModel):
    nom: str
    score: int

@app.post("/webhook/personnage")
def recevoir_webhook(p: PersonnageWebhook):
    if p.score >= 90:
        niveau = "Expert"
    elif p.score >= 70:
        niveau = "Confirmé"
    else:
        niveau = "Débutant"

    personnage_avec_niveau = {
        "nom": p.nom,
        "score": p.score,
        "niveau": niveau
    }

    try:
        if os.path.exists("webhook_log.json"):
            with open("webhook_log.json", "r+", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = []
                data.append(personnage_avec_niveau)
                f.seek(0)
                json.dump(data, f, ensure_ascii=False, indent=2)
        else:
            with open("webhook_log.json", "w", encoding="utf-8") as f:
                json.dump([personnage_avec_niveau], f, ensure_ascii=False, indent=2)
    except Exception as e:
        return {"erreur": str(e)}

    print(f"✅ Personnage ajouté avec succès : {personnage_avec_niveau['nom']}")
    with open("notifications.txt", "a", encoding="utf-8") as notif_file:
        notif_file.write(f"Personnage ajouté : {personnage_avec_niveau['nom']} ({personnage_avec_niveau['niveau']})\n")

    return personnage_avec_niveau
@app.post("/traitement")
async def traitement(personnage: dict):
    score = personnage.get("score", 0)
    niveau = "Débutant"
    if score >= 90:
        niveau = "Expert"
    elif score >= 70:
        niveau = "Confirmé"

    personnage["niveau"] = niveau
    return personnage
@app.get("/traitement/batch")
def traiter_tous_les_personnages():
    try:
        with open("webhook_log.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return {"erreur": "Fichier webhook_log.json introuvable"}
    except json.JSONDecodeError:
        return {"erreur": "Fichier JSON invalide"}

    for personnage in data:
        response = requests.post("http://127.0.0.1:8000/traitement", json=personnage)
        if response.status_code == 200:
            resultat = response.json()
        print(f"✅ {resultat['nom']} : score = {resultat['score']}, niveau = {resultat['niveau']}")
    else:
         print(f"❌ Erreur pour {personnage['nom']}")

    
    return {"message": "Traitement terminé"}
