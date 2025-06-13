from django.contrib import admin
from .models import (
    CategoriaCapacitacion, CursoTaller, InscripcionCurso, HistorialVisualizacion,
    DocumentoTecnico, HistorialDocumento, ValoracionDocumento
)

@admin.register(CategoriaCapacitacion)
class CategoriaCapacitacionAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'activo', 'orden', 'fecha_creacion']
    list_filter = ['activo']
    search_fields = ['nombre', 'descripcion']
    ordering = ['orden', 'nombre']

@admin.register(CursoTaller)
class CursoTallerAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'tipo', 'categoria', 'instructor', 'estado', 'destacado', 'vistas']
    list_filter = ['tipo', 'categoria', 'estado', 'dificultad', 'modalidad', 'destacado']
    search_fields = ['titulo', 'instructor', 'descripcion']
    readonly_fields = ['youtube_video_id', 'vistas', 'fecha_creacion', 'fecha_modificacion']
    filter_horizontal = []
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('titulo', 'descripcion', 'tipo', 'categoria', 'instructor')
        }),
        ('Configuración', {
            'fields': ('duracion_horas', 'duracion_minutos', 'dificultad', 'modalidad')
        }),
        ('Enlaces', {
            'fields': ('enlace_youtube', 'youtube_video_id')
        }),
        ('Contenido', {
            'fields': ('objetivos', 'requisitos', 'contenido_temas')
        }),
        ('Programación', {
            'fields': ('fecha_programada', 'fecha_limite_inscripcion', 'max_participantes')
        }),
        ('Control', {
            'fields': ('estado', 'destacado', 'certificacion_disponible', 'puntos_capacitacion')
        }),
        ('Metadatos', {
            'fields': ('etiquetas', 'autor', 'vistas', 'fecha_creacion', 'fecha_modificacion'),
            'classes': ('collapse',)
        }),
    )

@admin.register(DocumentoTecnico)
class DocumentoTecnicoAdmin(admin.ModelAdmin):
    list_display = [
        'titulo', 'tipo', 'categoria', 'autor_documento', 'version', 
        'estado', 'confidencialidad', 'vistas', 'descargas'
    ]
    list_filter = [
        'tipo', 'categoria', 'estado', 'confidencialidad', 'dificultad',
        'es_obligatorio', 'requiere_actualizacion'
    ]
    search_fields = ['titulo', 'autor_documento', 'descripcion', 'palabras_clave']
    readonly_fields = [
        'codigo_documento', 'slug', 'tamaño_archivo', 'vistas', 'descargas',
        'valoracion_promedio', 'fecha_creacion', 'fecha_modificacion', 'fecha_publicacion'
    ]
    filter_horizontal = ['documentos_relacionados']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('titulo', 'slug', 'descripcion', 'tipo', 'categoria')
        }),
        ('Archivo y Formato', {
            'fields': ('archivo_principal', 'formato', 'tamaño_archivo')
        }),
        ('Información Técnica', {
            'fields': (
                'autor_documento', 'revisor', 'version', 'codigo_documento',
                'dificultad', 'confidencialidad'
            )
        }),
        ('Fechas', {
            'fields': (
                'fecha_creacion_documento', 'fecha_revision', 'fecha_vencimiento',
                'fecha_creacion', 'fecha_modificacion', 'fecha_publicacion'
            )
        }),
        ('Control', {
            'fields': (
                'estado', 'es_obligatorio', 'requiere_actualizacion'
            )
        }),
        ('Contenido Adicional', {
            'fields': ('contenido_html', 'resumen_ejecutivo', 'palabras_clave'),
            'classes': ('collapse',)
        }),
        ('Objetivos y Aplicación', {
            'fields': ('objetivos', 'aplicacion', 'prerequisitos'),
            'classes': ('collapse',)
        }),
        ('Relacionamiento', {
            'fields': ('documentos_relacionados',),
            'classes': ('collapse',)
        }),
        ('Estadísticas', {
            'fields': ('vistas', 'descargas', 'valoracion_promedio'),
            'classes': ('collapse',)
        }),
    )

@admin.register(InscripcionCurso)
class InscripcionCursoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'curso', 'estado', 'progreso_porcentaje', 'fecha_inscripcion']
    list_filter = ['estado', 'curso__categoria', 'fecha_inscripcion']
    search_fields = ['usuario__username', 'curso__titulo']

@admin.register(HistorialVisualizacion)
class HistorialVisualizacionAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'curso', 'fecha_visualizacion', 'tiempo_visualizado']
    list_filter = ['fecha_visualizacion']
    search_fields = ['usuario__username', 'curso__titulo']

@admin.register(HistorialDocumento)
class HistorialDocumentoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'documento', 'accion', 'fecha']
    list_filter = ['accion', 'fecha']
    search_fields = ['usuario__username', 'documento__titulo', 'descripcion']
    readonly_fields = ['fecha']

@admin.register(ValoracionDocumento)
class ValoracionDocumentoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'documento', 'valoracion', 'fecha']
    list_filter = ['valoracion', 'fecha']
    search_fields = ['usuario__username', 'documento__titulo', 'comentario']
