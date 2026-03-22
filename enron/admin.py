from django.contrib import admin
from .models import Message, Collaborateur

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id_message', 'objet', 'date')

@admin.register(Collaborateur)
class CollaborateurAdmin(admin.ModelAdmin):
    list_display = ('id_collaborateur', 'mail')
