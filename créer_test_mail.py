import os
import random
import shutil
from pathlib import Path

source_root = Path(r"D:\enron_mail_20150507\maildir")
destination_dir = Path("test_mail")

#on regarde que le dossier test existe
destination_dir = Path("test_mail")
if not destination_dir.exists():
    destination_dir.mkdir()
else:
    print("Le dossier 'test_mail' existe déjà, on continue...")

#on prend tous les mails pour pouvoir en prendre aléatoirement
print("Début du téléchargement") #visuel pour voir l'avancé de l'action
all_files = []
for root, dirs, files in os.walk(source_root):
    for f in files:
        all_files.append(os.path.join(root, f))
    if len(all_files) % 20000 == 0:
        print(f"{len(all_files)} fichiers")#visuel 

print(f"Total : {len(all_files)} fichiers trouvés.")#visuel

#tirage aléatoire de 50 mails
selection = random.sample(all_files, min(50, len(all_files)))


for f_path in selection:
    f_path = Path(f_path)
    #on recréée le chemin test_mail/utilisateur/dossier/fichier
    relative_path = f_path.relative_to(source_root)
    dest_path = destination_dir / relative_path
    
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    chemin_source_long = "\\\\?\\" + str(f_path.absolute()) #\\\\?\\ force l'ouverture 
    shutil.copyfile(chemin_source_long, dest_path)
    print(f"Copié : {relative_path}")

print("\nC'est fini!")