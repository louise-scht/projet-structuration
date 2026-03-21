import os
import re
import pandas as pd
from email.utils import parsedate_to_datetime
from sqlalchemy import create_engine

#1. Configuration
DB_URL = 'postgresql://postgres:mon_password@localhost:5432/postgres_test' #changer le chemin de la base de donnée si nécessaire
engine = create_engine(DB_URL)
SOURCE_DIR = r"D:\enron_mail_20150507\maildir" #changer le chemin de enron si nécessaire

#2. Fonction d'extraction enrichie
def parse_email(file_path, root_dir):
    try:
        folder_path = os.path.relpath(os.path.dirname(file_path), root_dir)
        owner_name = folder_path.split(os.sep)[0]
        
        with open("\\\\?\\" + file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
            #on regarde les données qui sont en début de mail et on les extraits
            date_m = re.search(r'^Date: (.*)', content, re.M)
            from_m = re.search(r'^From: (.*)', content, re.M)
            sub_m = re.search(r'^Subject: (.*)', content, re.M)
            to_m = re.search(r'^To: (.*)', content, re.M)
            cc_m = re.search(r'^Cc: (.*)', content, re.M)
            bcc_m = re.search(r'^Bcc: (.*)', content, re.M) 
            
            body = content.split('\n\n', 1)[1] if '\n\n' in content else ""

            return {
                'owner_folder': owner_name, 
                'dossier_chemin': folder_path,
                'date': parsedate_to_datetime(date_m.group(1).strip()) if date_m else None,
                'expediteur_mail': from_m.group(1).strip() if from_m else "inconnu@enron.com",
                'objet': sub_m.group(1).strip()[:255] if sub_m else "(Sans objet)",
                'corps_mail': body,
                'to_raw': to_m.group(1).strip() if to_m else "",
                'cc_raw': cc_m.group(1).strip() if cc_m else "",
                'bcc_raw': bcc_m.group(1).strip() if bcc_m else ""
            }
    except Exception:
        return None

#3. Lecture des fichiers
print("Phase 1 : Lecture des fichiers importés")
data = []
count = 0 #compteur pour voir l'avancement
for root, _, files in os.walk(SOURCE_DIR):
    for f in files:
        res = parse_email(os.path.join(root, f), SOURCE_DIR)
        if res:
            data.append(res)
            count += 1
            if count % 10000 == 0:
                print(f"{count} fichiers lus...")

df = pd.DataFrame(data)

#4. Remplissage des Tables

#A. Collaborateur (ID, Nom, Mail)
print("Phase 2 : Création des collaborateurs")
all_emails = pd.concat([
    df['expediteur_mail'], 
    df['to_raw'].str.split(',').explode().str.strip(),
    df['cc_raw'].str.split(',').explode().str.strip(),
    df['bcc_raw'].str.split(',').explode().str.strip()
]).unique()#pour créer un collaborateur unique

collabs = pd.DataFrame([e for e in all_emails if e and '@' in str(e)], columns=['mail'])
collabs['id_collaborateur'] = range(1, len(collabs) + 1)
# On génère un nom propre à partir du mail pour la liaison dossier
collabs['nom_collaborateur'] = collabs['mail'].str.split('@').str[0].str.replace('.', '-', regex=False)
collabs.to_sql('collaborateur', engine, if_exists='replace', index=False)

#B. dossier 
print("Phase 3 : Création des dossiers")
dossiers = df[['dossier_chemin', 'owner_folder']].drop_duplicates().reset_index(drop=True)
dossiers['id_dossier'] = range(1, len(dossiers) + 1)
dossiers = dossiers.rename(columns={'owner_folder': 'nom_dossier', 'dossier_chemin': 'chemin_complet'})

#liaison avec id_collaborateur pour identifier celui qui gère le dossier
dossiers = dossiers.merge(
    collabs[['nom_collaborateur', 'id_collaborateur']], 
    left_on='nom_dossier', 
    right_on='nom_collaborateur', 
    how='left'
)
dossiers[['id_dossier', 'nom_dossier', 'id_collaborateur', 'chemin_complet']].to_sql('dossier', engine, if_exists='replace', index=False)

#C. Message 
print("Phase 4 : Insertion des messages")
df_msg = df.merge(collabs[['mail', 'id_collaborateur']], left_on='expediteur_mail', right_on='mail')
df_msg = df_msg.merge(dossiers[['chemin_complet', 'id_dossier']], left_on='dossier_chemin', right_on='chemin_complet')

messages = pd.DataFrame()
messages['id_message'] = range(1, len(df_msg) + 1)
messages['id_expediteur'] = df_msg['id_collaborateur']
messages['id_dossier'] = df_msg['id_dossier']
messages['objet'] = df_msg['objet']
messages['date'] = df_msg['date']
messages['corps_mail'] = df_msg['corps_mail']


messages.to_sql('message', engine, if_exists='replace', index=False)

#D. Destinataire
print("Phase 5 : Décollage des destinataires")
def process_dest(df_in, col_raw, type_env, msg_ids):
    temp = pd.DataFrame({'raw': df_in[col_raw], 'id_message': msg_ids})
    temp['email'] = temp['raw'].str.split(',')
    exploded = temp.explode('email').dropna(subset=['email'])
    exploded['email'] = exploded['email'].str.strip()
    exploded = exploded[exploded['email'].str.len() > 5]
    
    #liaison pour obtenir l'id_collaborateur du destinataire
    exploded = exploded.merge(collabs[['mail', 'id_collaborateur']], left_on='email', right_on='mail', how='left')
    return exploded[['id_message', 'id_collaborateur']].assign(type_envoie=type_env)

msg_ids = messages['id_message']
dest_to = process_dest(df_msg, 'to_raw', 'To', msg_ids)
dest_cc = process_dest(df_msg, 'cc_raw', 'Cc', msg_ids)
dest_bcc = process_dest(df_msg, 'bcc_raw', 'Bcc', msg_ids) 

destinataires = pd.concat([dest_to, dest_cc, dest_bcc], ignore_index=True)
destinataires['id_destinataire'] = range(1, len(destinataires) + 1)
destinataires.to_sql('destinataire', engine, if_exists='replace', index=False)

print(f"Fichiers importés!")