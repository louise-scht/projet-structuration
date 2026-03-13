import re
import os

def parse_email(contenu):
    # Regex pour extraire les métadonnées
    data = {
        'from': re.search(r'^From: (.*)', contenu, re.M),
        'to': re.search(r'^To: (.*)', contenu, re.M),
        'subject': re.search(r'^Subject: (.*)', contenu, re.M),
        'date': re.search(r'^Date: (.*)', contenu, re.M),
        'body': re.split(r'\n\n', contenu, maxsplit=1)
    }
    
    # Nettoyage des résultats
    return {
        'from': data['from'].group(1) if data['from'] else "Unknown",
        'to': data['to'].group(1) if data['to'] else "Unknown",
        'subject': data['subject'].group(1) if data['subject'] else "No Subject",
        'date': data['date'].group(1) if data['date'] else None,
        'body': data['body'][1] if len(data['body']) > 1 else ""
    }

# Exemple d'utilisation sur vos fichiers
dossier = r"D:\test_mail"
for nom in os.listdir(dossier):
    with open(os.path.join(dossier, nom), 'r', encoding='utf-8', errors='ignore') as f:
        info = parse_email(f.read())
        print(f"Mail: {nom} | De: {info['from']} | Objet: {info['subject']}")
        # Ici, vous pourriez appeler votre fonction d'insertion SQL