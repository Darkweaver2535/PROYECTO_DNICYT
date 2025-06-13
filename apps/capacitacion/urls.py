from django.urls import path
from . import views

app_name = 'capacitacion'

urlpatterns = [
    # Vista principal de biblioteca
    path('', views.biblioteca_cursos_view, name='biblioteca-cursos'),
    path('cursos-talleres/', views.biblioteca_cursos_view, name='cursos-talleres'),
    
    # Videos y multimedia
    path('videos-multimedia/', views.videos_multimedia_view, name='videos-multimedia'),
    path('video/<int:video_id>/reproducir/', views.reproducir_video_view, name='reproducir-video'),
    
    # ✅ DOCUMENTOS TÉCNICOS COMPLETAMENTE FUNCIONALES
    path('documentos-tecnicos/', views.documentos_tecnicos_view, name='documentos-tecnicos'),
    path('documento/<int:documento_id>/ver/', views.ver_documento_view, name='ver-documento'),
    path('documento/crear/', views.crear_documento_view, name='crear-documento'),
    path('documento/<int:documento_id>/editar/', views.editar_documento_view, name='editar-documento'),
    path('documento/<int:documento_id>/eliminar/', views.eliminar_documento_view, name='eliminar-documento'),
    path('documento/<int:documento_id>/descargar/', views.descargar_documento_view, name='descargar-documento'),
    path('documento/<int:documento_id>/valorar/', views.valorar_documento_view, name='valorar-documento'),
    path('documentos/gestionar/', views.gestionar_documentos_view, name='gestionar-documentos'),
    
    # Gestión de cursos (mantener existentes)
    path('curso/<int:curso_id>/', views.detalle_curso_view, name='detalle-curso'),
    path('crear/', views.crear_curso_view, name='crear-curso'),
    path('curso/<int:curso_id>/editar/', views.editar_curso_view, name='editar-curso'),
    path('curso/<int:curso_id>/eliminar/', views.eliminar_curso_view, name='eliminar-curso'),
    
    # Inscripciones
    path('curso/<int:curso_id>/inscribirse/', views.inscribirse_curso_view, name='inscribirse-curso'),
    path('mis-cursos/', views.mis_cursos_view, name='mis-cursos'),
    
    # Gestión administrativa
    path('categorias/', views.gestionar_categorias_view, name='gestionar-categorias'),
    
    # APIs
    path('api/curso/<int:curso_id>/stats/', views.api_curso_stats, name='api-curso-stats'),
    path('api/documento/<int:documento_id>/stats/', views.api_documento_stats, name='api-documento-stats'),
]