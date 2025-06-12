from django.contrib import admin
from .models import ReporteGenerado, AnalisisEquipos

@admin.register(ReporteGenerado)
class ReporteGeneradoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'tipo_reporte', 'formato', 'usuario', 'fecha_generacion', 'total_registros']
    list_filter = ['tipo_reporte', 'formato', 'fecha_generacion', 'usuario']
    search_fields = ['titulo', 'usuario__username']
    readonly_fields = ['fecha_generacion', 'tiempo_generacion']
    
    def has_add_permission(self, request):
        return False

@admin.register(AnalisisEquipos)
class AnalisisEquiposAdmin(admin.ModelAdmin):
    list_display = ['fecha_analisis', 'total_equipos', 'equipos_operativos', 'disponibilidad_promedio']
    list_filter = ['fecha_analisis']
    readonly_fields = ['fecha_analisis']
    
    def has_add_permission(self, request):
        return False