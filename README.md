#  Projet Enron Email 

Ce projet est une plateforme d'analyse et de visualisation du dataset Enron (500 000+ e-mails). 

## Installation et lancement

1. On vide Docker Desktop, on veut que la liste sooit vide (appuyer sur la corbeille).
2. Si il y a des fichiers db.sqlite3, on les supprime. 
3. On ferme les termianals ouvert. 
4. Téléchager le fichier Projet_Louise_Ileana.zip
5. Sur VsCode, on ouvre le dossier. Ensuite, dans le terminal on tape: 
```bash
docker-compose up --build -d
```
puis,
il faut créer une base de donnée avec le bon nom 

```bash
docker-compose exec db psql -U postgres -c "CREATE DATABASE postgres_test;"
```
puis,
```bash
docker-compose exec db psql -U postgres -d postgres_test -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;"
```
puis, 

```bash
py manage.py migrate
```
puis, (attention, cette commande prend du temps, environ 3-4 minutes. Ne pas quitter tant que le terminal n'a pas rendu la main)
```bash
cmd /c "docker-compose exec -T db psql -U postgres -d postgres_test < ./initdb/init_db_clean.sql"
```
et ensuite, 
```bash
py manage.py runserver
```
6. Ctrl+clic que le lien donné par runserver ("http://127.0.0.1:8000/")

7. Le site s'affiche dans le navigateur par défaut, certaines actions demandent du temps. 