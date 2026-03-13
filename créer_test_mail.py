from pathlib import Path
import shutil

# On garde le préfixe ici
source_dir = Path(r"\\?\D:\enron_mail_20150507\maildir\allen-p\_sent_mail")
destination_dir = Path("test_mail")

destination_dir.mkdir(exist_ok=True)

compteur = 0
limite = 10

print("Début de la copie...")

for fichier in source_dir.iterdir():
    if fichier.is_file() and compteur < limite:
        nom_dest = f"mail_{compteur + 1}.eml"
        dest_path = destination_dir / nom_dest
        
        # On force la conversion en chaîne de caractères avec le préfixe
        # Cela garantit que shutil reçoit le chemin "forcé"
        shutil.copyfile(str(fichier), str(dest_path))
        
        print(f"Copié : {fichier.name} -> {nom_dest}")
        compteur += 1

print(f"\nTerminé ! {compteur} emails ont été copiés.")