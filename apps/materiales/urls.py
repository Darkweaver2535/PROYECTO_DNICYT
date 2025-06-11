from django.urls import path
from . import views

app_name = 'materiales'

urlpatterns = [
    # Vista principal de materiales
    path('', views.materiales_view, name='materiales'),
    
    # CRUD de materiales
    path('crear/', views.crear_material_view, name='crear-material'),
    path('detalle/<int:pk>/', views.material_detalle_view, name='material-detalle'),
    path('editar/<int:pk>/', views.editar_material_view, name='editar-material'),
    path('eliminar/<int:pk>/', views.eliminar_material_view, name='eliminar-material'),
    
    # Movimientos de materiales
    path('movimiento/<int:pk>/', views.crear_movimiento_view, name='crear-movimiento'),
    
    # Exportaciones
    path('exportar-excel/', views.exportar_excel_view, name='exportar-excel'),
    path('exportar-pdf/', views.exportar_pdf_view, name='exportar-pdf'),
    path('exportar-csv/', views.exportar_csv_view, name='exportar-csv'),

    path('proveedores/', views.proveedores_view, name='proveedores'),

]