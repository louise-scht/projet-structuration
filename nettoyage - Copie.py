import re
import os

dossier_test = r"D:\test_mail"

# Regex expliquée : 
# ([\s\S]*?) : Capture tout (le corps du message)
# \n\n : cherche la première occurrence d'une ligne vide
# flags=re.MULTILINE : permet de traiter tout le fichier comme un bloc
regex_corps = re.compile(r'\n\n([\s\S]*)')

for nom_fichier in os.listdir(dossier_test):
    if nom_fichier.endswith(".eml"):
        chemin = os.path.join(dossier_test, nom_fichier)
        
        with open(chemin, 'r', encoding='utf-8', errors='ignore') as f:
            contenu = f.read()
            
            # Recherche avec la regex
            match = regex_corps.search(contenu)
            
            if match:
                corps = match.group(1).strip()
                print(f"\n--- Corps de {nom_fichier} ---")
                print(corps[:200]) # Affiche les 200 premiers caractères du corps