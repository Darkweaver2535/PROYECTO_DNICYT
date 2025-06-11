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
    path('exportar-repuestos/', views.exportar_repuestos_view, name='exportar-repuestos'),
    
    # URLs futuras
    # path('movimientos/', views.movimientos_view, name='movimientos'),
    # path('categorias/', views.categorias_view, name='categorias'),
    # path('proveedores/', views.proveedores_view, name='proveedores'),
]