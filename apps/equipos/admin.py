# equipos/admin.py
from django.contrib import admin
from .models import Seccion, Equipo

@admin.register(Seccion)
class SeccionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'identificador', 'responsable')
    search_fields = ('nombre', 'identificador')
    list_filter = ('ubicacion',)

@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = ('codigo_interno', 'codigo_udb', 'nombre', 'seccion', 'estado', 'responsable')
    list_filter = ('seccion', 'estado', 'responsable')
    search_fields = ('codigo_interno', 'nombre', 'modelo', 'serie')
    readonly_fields = ('fecha_ingreso', 'qr_code')
    filter_horizontal = ('materiales_necesarios', 'herramientas_necesarias')  # Añadir esta línea
    fieldsets = (
        ('Identificación', {
            'fields': ('codigo_udb', 'codigo_interno', 'nombre', 'modelo', 'serie', 'fabricante', 'año_fabricacion')
        }),
        ('Características Técnicas', {
            'fields': ('potencia', 'capacidad', 'tipo_equipo')
        }),
        ('Especificaciones Eléctricas', {
            'fields': ('voltaje', 'amperaje', 'fases', 'frecuencia', 'consumo_electrico')
        }),
        ('Materiales y Herramientas', {  # Añadir esta sección
            'fields': ('materiales_necesarios', 'herramientas_necesarias')
        }),
        ('Ubicación y Estado', {
            'fields': ('seccion', 'ubicacion_fisica', 'estado', 'responsable')
        }),
        ('Archivos', {
            'fields': ('foto', 'qr_code')
        }),
        ('Otros', {
            'fields': ('fecha_ingreso', 'observaciones')
        }),
    )