from django.contrib import admin
from .models import PlanMantenimiento, TareaMantenimiento, RepuestoCritico

@admin.register(RepuestoCritico)
class RepuestoCriticoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'codigo_fabricante', 'stock_minimo', 'proveedor', 'costo_unitario']
    search_fields = ['nombre', 'codigo_fabricante', 'proveedor']
    list_filter = ['proveedor', 'tiempo_entrega']

@admin.register(PlanMantenimiento)
class PlanMantenimientoAdmin(admin.ModelAdmin):
    list_display = ['codigo_plan', 'nombre', 'equipo', 'tipo_mantenimiento', 'frecuencia', 'estado', 'proxima_ejecucion', 'eficiencia_promedio']
    list_filter = ['tipo_mantenimiento', 'frecuencia', 'estado', 'prioridad', 'cumple_iso', 'norma_aplicable']
    search_fields = ['codigo_plan', 'nombre', 'equipo__nombre', 'equipo__codigo_interno']
    readonly_fields = ['codigo_plan', 'numero_ejecuciones', 'tiempo_promedio_ejecucion', 'eficiencia_promedio']
    filter_horizontal = ['repuestos_criticos', 'responsables_secundarios']

@admin.register(TareaMantenimiento)
class TareaMantenimientoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'plan', 'orden', 'estado', 'es_critica']
    list_filter = ['estado', 'es_critica', 'requiere_verificacion']
    search_fields = ['nombre', 'plan__nombre', 'plan__codigo_plan']
