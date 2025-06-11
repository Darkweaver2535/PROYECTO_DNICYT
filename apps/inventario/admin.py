from django.contrib import admin
from .models import Repuesto, CategoriaRepuesto, Proveedor, MovimientoStock

@admin.register(CategoriaRepuesto)
class CategoriaRepuestoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'activo']
    list_filter = ['activo']
    search_fields = ['codigo', 'nombre']

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'contacto_principal', 'calificacion', 'activo']
    list_filter = ['activo', 'calificacion', 'pais']
    search_fields = ['codigo', 'nombre', 'contacto_principal']

@admin.register(Repuesto)
class RepuestoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'categoria', 'stock_actual', 'estado', 'criticidad']
    list_filter = ['estado', 'criticidad', 'categoria', 'es_consumible']
    search_fields = ['codigo', 'nombre', 'descripcion', 'codigo_fabricante']
    readonly_fields = ['codigo', 'fecha_creacion', 'fecha_actualizacion']

@admin.register(MovimientoStock)
class MovimientoStockAdmin(admin.ModelAdmin):
    list_display = ['repuesto', 'tipo_movimiento', 'cantidad', 'fecha_movimiento', 'usuario']
    list_filter = ['tipo_movimiento', 'fecha_movimiento']
    search_fields = ['repuesto__codigo', 'repuesto__nombre', 'motivo']
    readonly_fields = ['fecha_movimiento']