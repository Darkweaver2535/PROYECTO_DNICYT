from django.contrib import admin
from .models import (
    CategoriaSeguridad, NormativaSeguridad, InspeccionSeguridad,
    IncidenteSeguridad, HistorialNormativa, CapacitacionSeguridad,
    ParticipacionCapacitacion
)

@admin.register(CategoriaSeguridad)
class CategoriaSeguridadAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'orden', 'es_critica', 'activo', 'fecha_creacion']
    list_filter = ['es_critica', 'activo']
    search_fields = ['nombre', 'descripcion']
    ordering = ['orden', 'nombre']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'descripcion')
        }),
        ('Configuración Visual', {
            'fields': ('color_hex', 'icono', 'orden')
        }),
        ('Configuración', {
            'fields': ('es_critica', 'activo')
        }),
    )

@admin.register(NormativaSeguridad)
class NormativaSeguridadAdmin(admin.ModelAdmin):
    list_display = [
        'codigo', 'titulo', 'tipo', 'categoria', 'prioridad', 
        'estado', 'fecha_vigencia_inicio', 'vistas'
    ]
    list_filter = [
        'tipo', 'categoria', 'prioridad', 'estado', 
        'es_obligatoria', 'requiere_capacitacion'
    ]
    search_fields = ['titulo', 'codigo', 'descripcion', 'palabras_clave']
    readonly_fields = [
        'codigo', 'slug', 'vistas', 'descargas', 'fecha_creacion', 
        'fecha_modificacion', 'fecha_publicacion'
    ]
    filter_horizontal = ['normativas_relacionadas']
    date_hierarchy = 'fecha_vigencia_inicio'

@admin.register(InspeccionSeguridad)
class InspeccionSeguridadAdmin(admin.ModelAdmin):
    list_display = [
        'normativa', 'inspector', 'tipo_inspeccion', 'resultado', 
        'puntuacion', 'fecha_inspeccion', 'corregido'
    ]
    list_filter = ['tipo_inspeccion', 'resultado', 'corregido']
    search_fields = ['normativa__titulo', 'inspector__username', 'area_inspeccionada']
    date_hierarchy = 'fecha_inspeccion'

@admin.register(IncidenteSeguridad)
class IncidenteSeguridadAdmin(admin.ModelAdmin):
    list_display = [
        'numero_incidente', 'tipo_incidente', 'gravedad', 'area_afectada',
        'reportado_por', 'fecha_incidente', 'estado'
    ]
    list_filter = ['tipo_incidente', 'gravedad', 'estado']
    search_fields = ['numero_incidente', 'descripcion_incidente', 'area_afectada']
    readonly_fields = ['numero_incidente']
    date_hierarchy = 'fecha_incidente'
    filter_horizontal = ['normativas_incumplidas']

@admin.register(HistorialNormativa)
class HistorialNormativaAdmin(admin.ModelAdmin):
    list_display = ['normativa', 'usuario', 'accion', 'fecha']
    list_filter = ['accion', 'fecha']
    search_fields = ['normativa__titulo', 'usuario__username', 'descripcion']
    readonly_fields = ['fecha']
    date_hierarchy = 'fecha'

@admin.register(CapacitacionSeguridad)
class CapacitacionSeguridadAdmin(admin.ModelAdmin):
    list_display = [
        'titulo', 'modalidad', 'fecha_inicio', 'fecha_fin', 
        'instructor', 'max_participantes', 'estado'
    ]
    list_filter = ['modalidad', 'estado', 'es_obligatoria', 'certificacion']
    search_fields = ['titulo', 'instructor', 'descripcion']
    filter_horizontal = ['normativas_cubiertas']
    date_hierarchy = 'fecha_inicio'

@admin.register(ParticipacionCapacitacion)
class ParticipacionCapacitacionAdmin(admin.ModelAdmin):
    list_display = [
        'participante', 'capacitacion', 'estado', 'calificacion', 
        'certificado_otorgado', 'fecha_inscripcion'
    ]
    list_filter = ['estado', 'certificado_otorgado']
    search_fields = ['participante__username', 'capacitacion__titulo']
    date_hierarchy = 'fecha_inscripcion'
