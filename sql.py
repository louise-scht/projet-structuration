import os
import re
import psycopg2
from psycopg2.extras import execute_values

# Connexion à votre base Docker
conn = psycopg2.connect(dbname="postgres", user="postgres", password="mon_password", host="localhost", port="5432")
cur = conn.cursor()

# Création de la table (si elle n'existe pas)
cur.execute("""
    CREATE TABLE IF NOT EXISTS emails (
        id SERIAL PRIMARY KEY,
        sender VARCHAR(255),
        recipient VARCHAR(255),
        subject TEXT,
        body TEXT
    )
""")

def extraire_donnees(chemin_fichier):
    with open(chemin_fichier, 'r', encoding='utf-8', errors='ignore') as f:
        contenu = f.read()
        # Extraction simplifiée
        match_from = re.search(r'^From: (.*)', contenu, re.M)
        match_to = re.search(r'^To: (.*)', contenu, re.M)
        match_sub = re.search(r'^Subject: (.*)', contenu, re.M)
        body_split = re.split(r'\n\n', contenu, maxsplit=1)
        
        return (
            match_from.group(1) if match_from else "N/A",
            match_to.group(1) if match_to else "N/A",
            match_sub.group(1) if match_sub else "N/A",
            body_split[1] if len(body_split) > 1 else ""
        )

# Traitement par paquets (batch de 100)
source = r"\\?\D:\enron_mail_20150507\maildir\allen-p\_sent_mail"
liste_mails = [os.path.join(source, f) for f in os.listdir(source) if f.endswith(".")]

batch = []
for f in liste_mails:
    batch.append(extraire_donnees(f))
    if len(batch) >= 100: # Toutes les 100 insertions, on envoie à la base
        execute_values(cur, "INSERT INTO emails (sender, recipient, subject, body) VALUES %s", batch)
        conn.commit()
        print(f"100 mails insérés...")
        batch = []

# Insérer le reste
if batch:
    execute_values(cur, "INSERT INTO emails (sender, recipient, subject, body) VALUES %s", batch)
    conn.commit()

print("Importation terminée avec succès !")
conn.close()