from django.contrib import admin
from .models import Material, CategoriaMaterial, MovimientoMaterial

@admin.register(CategoriaMaterial)
class CategoriaMaterialAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'tipo_categoria', 'activo']
    list_filter = ['tipo_categoria', 'activo']
    search_fields = ['codigo', 'nombre']
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        
        # Crear categorías de herramientas automáticamente si no existen
        if not change:  # Solo al crear nuevas categorías
            categorias_herramientas = [
                {
                    'codigo': 'HM001',
                    'nombre': 'Herramientas Manuales de Precisión',
                    'tipo_categoria': 'herramientas_manuales',
                    'descripcion': 'Herramientas manuales para trabajos de precisión'
                },
                {
                    'codigo': 'HE001',
                    'nombre': 'Herramientas Eléctricas Portátiles',
                    'tipo_categoria': 'herramientas_electricas',
                    'descripcion': 'Herramientas eléctricas portátiles para uso general'
                },
                {
                    'codigo': 'IM001',
                    'nombre': 'Instrumentos de Medición Digital',
                    'tipo_categoria': 'instrumentos_medicion',
                    'descripcion': 'Instrumentos digitales para medición y control'
                },
                {
                    'codigo': 'HP001',
                    'nombre': 'Herramientas de Precisión Industrial',
                    'tipo_categoria': 'herramientas_precision',
                    'descripcion': 'Herramientas de alta precisión para manufactura'
                },
                {
                    'codigo': 'HC001',
                    'nombre': 'Herramientas de Corte y Desbaste',
                    'tipo_categoria': 'herramientas_corte',
                    'descripcion': 'Herramientas para corte, desbaste y acabado'
                },
                {
                    'codigo': 'EL001',
                    'nombre': 'Equipos de Laboratorio',
                    'tipo_categoria': 'equipos_laboratorio',
                    'descripcion': 'Equipos especializados para laboratorio'
                },
            ]
            
            for cat_data in categorias_herramientas:
                if not CategoriaMaterial.objects.filter(codigo=cat_data['codigo']).exists():
                    CategoriaMaterial.objects.create(**cat_data)

# ✅ REMOVER EL @admin.register DUPLICADO - USAR SOLO UNO
class MaterialAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'tipo', 'categoria', 'stock_actual', 'estado', 'criticidad']
    list_filter = ['tipo', 'estado', 'criticidad', 'categoria', 'activo']
    search_fields = ['codigo', 'nombre', 'descripcion', 'marca', 'modelo']
    readonly_fields = ['codigo', 'fecha_creacion', 'fecha_actualizacion']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo', 'nombre', 'descripcion', 'tipo', 'categoria')
        }),
        ('Identificación', {
            'fields': ('marca', 'modelo', 'numero_parte', 'codigo_barras')
        }),
        ('Inventario', {
            'fields': ('stock_actual', 'stock_minimo', 'stock_maximo', 'punto_reorden', 'unidad_medida')
        }),
        ('Costos', {
            'fields': ('precio_unitario',)
        }),
        ('Clasificación', {
            'fields': ('estado', 'criticidad', 'ubicacion', 'proveedor_principal')
        }),
        ('Características Especiales', {
            'fields': ('requiere_refrigeracion', 'requiere_manejo_especial')
        }),
        ('Herramientas - Características Específicas', {
            'fields': ('es_herramienta_critica', 'requiere_calibracion', 'fecha_ultima_calibracion', 
                      'frecuencia_calibracion', 'requiere_mantenimiento', 'fecha_ultimo_mantenimiento', 
                      'frecuencia_mantenimiento'),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('fecha_vencimiento', 'fecha_ultima_compra', 'fecha_creacion', 'fecha_actualizacion')
        }),
        ('Documentos', {
            'fields': ('foto', 'ficha_tecnica')
        }),
        ('Control', {
            'fields': ('activo',)
        }),
    )

# ✅ REGISTRAR MANUALMENTE EL MODELO MATERIAL
admin.site.register(Material, MaterialAdmin)

@admin.register(MovimientoMaterial)
class MovimientoMaterialAdmin(admin.ModelAdmin):
    list_display = ['numero_movimiento', 'material', 'tipo_movimiento', 'cantidad', 'fecha_movimiento', 'usuario']
    list_filter = ['tipo_movimiento', 'motivo', 'estado', 'fecha_movimiento']
    search_fields = ['numero_movimiento', 'material__codigo', 'material__nombre']
    readonly_fields = ['numero_movimiento', 'fecha_movimiento']

