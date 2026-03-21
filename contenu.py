# Affiche le contenu de l'email copié
destination = "test_mail/email_test.eml" 

with open(destination, 'r', encoding='utf-8', errors='ignore') as f:
    contenu = f.read()
    print("--- Contenu du mail ---")
    print(contenu[:500]) # On affiche les 500 premiers caractères