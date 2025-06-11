from django.contrib import admin
from .models import ProcedimientoOperativo, AnalisisRiesgo, MedidaControl

# ...existing admin registrations...

@admin.register(AnalisisRiesgo)
class AnalisisRiesgoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'descripcion', 'area', 'tipo', 'riesgo_actual', 'nivel_riesgo', 'estado', 'responsable', 'fecha_revision']
    list_filter = ['area', 'tipo', 'nivel_riesgo', 'estado', 'fecha_identificacion']
    search_fields = ['codigo', 'descripcion', 'responsable']
    readonly_fields = ['codigo', 'riesgo_actual', 'nivel_riesgo', 'fecha_creacion', 'fecha_actualizacion']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo', 'descripcion', 'area', 'tipo')
        }),
        ('Evaluación de Riesgo', {
            'fields': ('probabilidad', 'severidad', 'riesgo_actual', 'nivel_riesgo')
        }),
        ('Gestión', {
            'fields': ('estado', 'responsable', 'fecha_identificacion', 'fecha_revision')
        }),
        ('Medidas de Control', {
            'fields': ('medidas_control', 'recursos_necesarios', 'plazo_implementacion')
        }),
        ('Seguimiento', {
            'fields': ('fecha_ultima_revision', 'observaciones', 'equipo_asociado', 'identificado_por')
        }),
    )

@admin.register(MedidaControl)
class MedidaControlAdmin(admin.ModelAdmin):
    list_display = ['riesgo', 'descripcion', 'tipo_medida', 'estado', 'responsable', 'fecha_planificada']
    list_filter = ['tipo_medida', 'estado', 'fecha_planificada']
    search_fields = ['descripcion', 'responsable', 'riesgo__codigo']