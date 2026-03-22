from django.shortcuts import render, get_object_or_404
from datetime import timedelta
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from .models import Message, Collaborateur, Destinataire, TopMot

def accueil(request):
    #Récupération des paramètres
    query = request.GET.get('q', '')
    date_debut = request.GET.get('date_debut','')
    date_fin = request.GET.get('date_fin','')
    view_type = request.GET.get('view', 'messages') 
    page_number = request.GET.get('page', 1)

    #Base de la requête 
    messages_list = Message.objects.all().select_related('expediteur')

    #Application des filtres
    filters = Q()
    if query:
        filters &= (Q(objet__icontains=query) | Q(corps_mail__icontains=query) | Q(expediteur__nom_collaborateur__icontains=query))
    
    if date_debut:
        filters &= Q(date__gte=date_debut)
    if date_fin:
        filters &= Q(date__lte=date_fin)

    page_obj = None
    top_data = None

    #Onglet
    if view_type == 'collabs':
        top_data = messages_list.values('expediteur__nom_collaborateur', 'expediteur__mail').annotate(total=Count('id_message')).order_by('-total')[:10]
    
    elif view_type == 'mots':
        top_data = TopMot.objects.all().order_by('-occurrence')[:10]

    elif view_type == 'echanges':
        top_data = Destinataire.objects.exclude(
            Q(message__expediteur__nom_collaborateur__icontains='pete') | 
            Q(message__expediteur__mail__icontains='pete.davis')
        ).values('message__expediteur__nom_collaborateur','collaborateur__nom_collaborateur').annotate(total=Count('id_destinataire')).order_by('-total')[:10]
    
    else:
        messages_list = messages_list.filter(filters).order_by('-id_message') 
        paginator = Paginator(messages_list, 50) 
        page_obj = paginator.get_page(page_number)
        view_type = 'messages'

    context = {
        'page_obj': page_obj, 'top_data': top_data, 'view_type': view_type,
        'query': query, 'date_debut' : date_debut, 'date_fin' : date_fin,
    }
    return render(request, 'enron/index.html', context)

def detail_message(request, message_id):
    message = get_object_or_404(Message.objects.select_related('expediteur'), id_message=message_id)
    destinataires = Destinataire.objects.filter(message=message).select_related('collaborateur')
    
    reponses = []
    precedents = []

    #on nettoie l'objet pour trouver la discussion
    objet_pur = message.objet.upper().replace('RE:', '').replace('FW:', '').strip()
    
    #on cherche les messages liés par l'objet
    discussion = Message.objects.filter(objet__icontains=objet_pur).exclude(id_message=message.id_message).select_related('expediteur').distinct('corps_mail')

    if message.date:
        #si on a une date, on sépare avant/après
        reponses = discussion.filter(date__gt=message.date).order_by('corps_mail','date')[:5]
        precedents = discussion.filter(date__lt=message.date).order_by('corps_mail','-date')[:5]
    else:
        #si pas de date, on montre juste les messages ayant le même objet
        reponses = discussion.order_by('corps_mail')[:10]

    return render(request, 'enron/detail.html', {
        'message': message, 'destinataires': destinataires,
        'reponses': reponses, 'precedents': precedents
    })

def statistiques_view(request):
    #on exclut les dates nulles uniquement pour les stats chronologiques
    qs_valide = Message.objects.exclude(date__isnull=True)

    stats_raw = qs_valide.annotate(
        mois=TruncMonth('date')
    ).values('mois').annotate(
        nb_messages=Count('id_message'),
        nb_expediteurs=Count('expediteur', distinct=True)
    ).order_by('-mois')

    stats_finales = []
    for s in stats_raw:
        current_mois = s['mois']
        if not current_mois: continue

        top_10 = qs_valide.filter(
            date__year=current_mois.year, 
            date__month=current_mois.month
        ).values('expediteur__nom_collaborateur', 'expediteur__mail').annotate(total=Count('id_message')).order_by('-total')[:10]

        intensite = s['nb_messages'] / s['nb_expediteurs'] if s['nb_expediteurs'] > 0 else 0
        
        stats_finales.append({
            'mois': current_mois,
            'nb_messages': s['nb_messages'],
            'nb_expediteurs': s['nb_expediteurs'],
            'intensite': round(intensite, 1),
            'top_10': top_10
        })

    return render(request, 'enron/stats.html', {'stats': stats_finales})