# equipos/admin.py
from django.contrib import admin
from .models import Seccion

@admin.register(Seccion)
class SeccionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'identificador', 'responsable')
    search_fields = ('nombre', 'identificador')
    list_filter = ('ubicacion',)