from django.urls import path
from . import views

app_name = 'inventario'

urlpatterns = [
    # Dashboard principal
    path('', views.dashboard_inventario_view, name='dashboard'),
    
    # Repuestos
    path('repuestos/', views.repuestos_view, name='repuestos'),
    path('repuesto/<int:pk>/', views.repuesto_detalle_view, name='repuesto-detalle'),
    path('crear-repuesto/', views.crear_repuesto_view, name='crear-repuesto'),
    path('editar-repuesto/<int:pk>/', views.editar_repuesto_view, name='editar-repuesto'),
    path('eliminar-repuesto/<int:pk>/', views.eliminar_repuesto_view, name='eliminar-repuesto'),
    path('exportar-repuestos/', views.exportar_repuestos_view, name='exportar-repuestos'),
    
    # Stock crítico
    path('stock-critico/', views.stock_critico_view, name='stock-critico'),
    path('api/alertas-stock/', views.alertas_stock_api, name='alertas-stock-api'),
    
    # Movimientos
    path('movimientos/', views.movimientos_stock_view, name='movimientos'),
    path('crear-movimiento/', views.crear_movimiento_view, name='crear-movimiento'),
    
    # Proveedores - ACTUALIZADAS
    path('proveedores/', views.proveedores_view, name='proveedores'),
    path('crear-proveedor/', views.crear_proveedor_view, name='crear-proveedor'),
    path('detalle-proveedor/<int:pk>/', views.detalle_proveedor_view, name='detalle-proveedor'),
    path('editar-proveedor/<int:pk>/', views.editar_proveedor_view, name='editar-proveedor'),
    path('eliminar-proveedor/<int:pk>/', views.eliminar_proveedor_view, name='eliminar-proveedor'),
]