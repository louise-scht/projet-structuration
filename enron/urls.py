from django.urls import path
from . import views

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('message/<int:message_id>/', views.detail_message, name='detail_message'),
    path('stats/', views.statistiques_view, name='statistiques_view'),
]

