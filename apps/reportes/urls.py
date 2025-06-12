from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    # Vista principal de reportes de equipos
    path('equipos/', views.reportes_equipos_view, name='reportes-equipos'),
    
    # Exportaciones
    path('equipos/exportar/excel/', views.exportar_reporte_equipos_excel, name='exportar-equipos-excel'),
    path('equipos/exportar/pdf/', views.exportar_reporte_equipos_pdf, name='exportar-equipos-pdf'),
    
    # APIs para gráficos
    path('api/equipos/chart-data/', views.api_equipos_chart_data, name='api-equipos-chart-data'),

    # Análisis de Fallas - URLS COMPLETAS
    path('analisis-fallas/', views.analisis_fallas_view, name='analisis-fallas'),
    path('crear-falla/', views.crear_falla_view, name='crear-falla'),
    path('falla/<str:codigo_falla>/', views.detalle_falla_view, name='detalle-falla'),
    path('editar-falla/<str:codigo_falla>/', views.editar_falla_view, name='editar-falla'),
    path('eliminar-falla/<str:codigo_falla>/', views.eliminar_falla_view, name='eliminar-falla'),
    path('cerrar-falla/<str:codigo_falla>/', views.cerrar_falla_view, name='cerrar-falla'),
    path('asignar-falla/<str:codigo_falla>/', views.asignar_falla_view, name='asignar-falla'),
]
