from django.core.management.base import BaseCommand
from enron.models import Message, TopMot
from collections import Counter
import re

class Command(BaseCommand):
    help = 'Analyse les mails pour générer le Top 10 des mots'

    def handle(self, *args, **options):
        self.stdout.write("Analyse des messages en cours")
        
        TopMot.objects.all().delete()

        #Liste de mots à exclure
        stop_words = {
            'the', 'to', 'and', 'of', 'a', 'in', 'for', 'is', 'on', 'that','these','their', 
            'this', 'it', 'with', 'from', 'be', 'are', 'have', 'your', 'at',
            'will', 'would', 'shall', 'please', 'thanks', 'thank', 'subject', 
            'from', 'sent', 'mailto', 'http', 'https', 'font', 'corp', 'company',
            'message', 'email', 'know', 'want', 'think', 'original','there','which','about','other','should'
        }

        
        messages = Message.objects.exclude(corps_mail__isnull=True).values_list('corps_mail', flat=True)
        
        compteur = Counter()

        for corps in messages:
            # On cherche des mots de 5 lettres minimum pour éviter les petits mots bateau
            mots = re.findall(r'\b[a-z]{5,}\b', corps.lower()) 
            mots_filtres = [m for m in mots if m not in stop_words]
            compteur.update(mots_filtres)

        # Enregistrement du Top 10
        for mot, occ in compteur.most_common(10):
            TopMot.objects.create(mot=mot, occurrence=occ)
            self.stdout.write(f"Mot trouvé : {mot} ({occ} fois)")

        self.stdout.write(self.style.SUCCESS('Félicitations ! Le Top 10 est prêt.'))