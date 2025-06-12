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
]