from django.db import models
from django.contrib.postgres.indexes import GinIndex

class Collaborateur(models.Model):
    id_collaborateur = models.AutoField(primary_key=True)
    mail = models.EmailField(max_length=255, unique=True)
    nom_collaborateur = models.CharField(max_length=255)

    class Meta:
        managed = True
        db_table = 'collaborateur'

class Dossier(models.Model):
    id_dossier = models.AutoField(primary_key=True)
    nom_dossier = models.CharField(max_length=255)
    chemin_complet = models.TextField()
    id_collaborateur = models.IntegerField(null=True)

    class Meta:
        managed = True
        db_table = 'dossier'

class Message(models.Model):
    id_message = models.AutoField(primary_key=True)
    expediteur = models.ForeignKey(
        Collaborateur, 
        on_delete=models.CASCADE, 
        db_column='id_expediteur',
        related_name='messages_envoyes'
    )
    dossier = models.ForeignKey(
        Dossier, 
        on_delete=models.CASCADE, 
        db_column='id_dossier'
    )
    objet = models.CharField(max_length=255,null=True)
    date = models.DateTimeField(null=True)
    corps_mail = models.TextField(null=True)

    class Meta:
        managed = True
        db_table = 'message'
        indexes = [
            GinIndex(
                fields=['corps_mail'], 
                name='corps_mail_gin_index', 
                opclasses=['gin_trgm_ops']  
            ),
            models.Index(fields=['date']), 
        ]

class Destinataire(models.Model):
    id_destinataire = models.AutoField(primary_key=True)
    #lien vers le message concerné
    message = models.ForeignKey(
        Message, 
        on_delete=models.CASCADE, 
        db_column='id_message',
        related_name='destinataires'
    )
    #lien vers le collaborateur qui reçoit
    collaborateur = models.ForeignKey(
        Collaborateur, 
        on_delete=models.CASCADE, 
        db_column='id_collaborateur',
        related_name='receptions'
    )
    type_envoie = models.CharField(max_length=10) 

    class Meta:
        managed = True
        db_table = 'destinataire'

class TopMot(models.Model):
    id_mot = models.AutoField(primary_key=True)
    mot = models.CharField(max_length=100, unique=True)
    occurrence = models.IntegerField()
    date_calcul = models.DateTimeField(auto_now=True) #pour savoir quand le top a été mis à jour

    class Meta:
        db_table = 'top_mot'
        ordering = ['-occurrence'] #les plus fréquents en premier

    def __str__(self):
        return f"{self.mot} ({self.occurrence})"


