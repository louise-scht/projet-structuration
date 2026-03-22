from django.shortcuts import render
from .models import site1
from .forms import RechercheForm

def liste_articles(request):
    articles = MonArticle.objects.all()
    form = RechercheForm(request.GET)

    if form.is_valid():
        if form.cleaned_data['mot_cle']:
            articles = articles.filter(titre__icontains=form.cleaned_data['mot_cle'])
        
        if form.cleaned_data['date_precise']:
            articles = articles.filter(date_publication__date=form.cleaned_data['date_precise'])

    return render(request, 'ton_app/liste.html', {'articles': articles, 'form': form})