from django.contrib import admin
from .models import Material, CategoriaMaterial, MovimientoMaterial

@admin.register(CategoriaMaterial)
class CategoriaMaterialAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'tipo_categoria', 'activo']
    list_filter = ['tipo_categoria', 'activo']
    search_fields = ['codigo', 'nombre']

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'tipo', 'categoria', 'stock_actual', 'estado', 'criticidad']
    list_filter = ['tipo', 'estado', 'criticidad', 'categoria', 'requiere_refrigeracion', 'requiere_manejo_especial']
    search_fields = ['codigo', 'nombre', 'descripcion', 'marca', 'modelo']
    readonly_fields = ['codigo', 'fecha_creacion', 'fecha_actualizacion']

@admin.register(MovimientoMaterial)
class MovimientoMaterialAdmin(admin.ModelAdmin):
    list_display = ['numero_movimiento', 'material', 'tipo_movimiento', 'cantidad', 'fecha_movimiento', 'usuario']
    list_filter = ['tipo_movimiento', 'motivo', 'estado', 'fecha_movimiento']
    search_fields = ['numero_movimiento', 'material__nombre', 'material__codigo']
    readonly_fields = ['numero_movimiento']