from django.urls import path
from . import views

app_name = 'materiales'

urlpatterns = [
    # URLs principales
    path('', views.materiales_view, name='materiales'),
    path('herramientas/', views.herramientas_view, name='herramientas'),
    
    # Crear
    path('crear-material/', views.crear_material_view, name='crear-material'),
    path('crear-herramienta/', views.crear_herramienta_view, name='crear-herramienta'),
    
    # Detalle
    path('material/<int:pk>/', views.material_detalle_view, name='material-detalle'),
    path('herramienta/<int:pk>/', views.herramienta_detalle_view, name='herramienta-detalle'),
    
    # Editar
    path('editar-material/<int:pk>/', views.editar_material_view, name='editar-material'),
    path('editar-herramienta/<int:pk>/', views.editar_herramienta_view, name='editar-herramienta'),
    
    # Eliminar
    path('eliminar-herramienta/<int:pk>/', views.eliminar_herramienta_view, name='eliminar-herramienta'),
    
    # Movimientos - CORREGIR ESTAS URLS
    path('movimientos/', views.movimientos_view, name='movimientos'),
    path('crear-movimiento/', views.crear_movimiento_view, name='crear-movimiento'),
    path('crear-movimiento/<int:material_pk>/', views.crear_movimiento_view, name='crear-movimiento-material'),
    
    # Exportaciones
    path('exportar-excel/', views.exportar_excel_view, name='exportar-excel'),
    path('exportar-pdf/', views.exportar_pdf_view, name='exportar-pdf'),
    path('exportar-csv/', views.exportar_csv_view, name='exportar-csv'),

    path('proveedores/', views.proveedores_view, name='proveedores'),
]