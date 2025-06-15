from django.urls import path
from . import views

app_name = 'normativas'

urlpatterns = [
    # Vista principal
    path('', views.normativas_view, name='normativas'),
    
    # ✅ VISTAS DE SEGURIDAD INDUSTRIAL Y ALERTAS
    path('seguridad-industrial/', views.seguridad_industrial_view, name='seguridad-industrial'),
    path('alertas-riesgos/', views.alertas_riesgos_view, name='alertas-riesgos'),
    
    # Gestión de normativas
    path('normativa/<int:normativa_id>/ver/', views.ver_normativa_view, name='ver-normativa'),
    path('normativa/crear/', views.crear_normativa_view, name='crear-normativa'),
    path('normativa/<int:normativa_id>/editar/', views.editar_normativa_view, name='editar-normativa'),
    path('normativa/<int:normativa_id>/descargar/', views.descargar_normativa_view, name='descargar-normativa'),
    
    # Incidentes de seguridad
    path('incidentes/', views.incidentes_view, name='incidentes'),
    path('incidente/crear/', views.crear_incidente_view, name='crear-incidente'),
    
    # Inspecciones
    path('inspecciones/', views.inspecciones_view, name='inspecciones'),
    
    # Capacitaciones
    path('capacitaciones/', views.capacitaciones_view, name='capacitaciones'),
    
    # Gestión administrativa
    path('gestionar/', views.gestionar_normativas_view, name='gestionar-normativas'),
    
    # APIs
    path('api/normativa/<int:normativa_id>/stats/', views.api_normativa_stats, name='api-normativa-stats'),
    path('api/dashboard-stats/', views.api_dashboard_stats, name='api-dashboard-stats'),
]