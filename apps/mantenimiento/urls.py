from django.urls import path
from . import views

app_name = 'mantenimiento'

urlpatterns = [
    # Planes de Mantenimiento
    path('planes/', views.planes_mantenimiento_view, name='planes-mantenimiento'),
    path('planes/crear/', views.crear_plan_view, name='crear-plan'),
    path('planes/editar/<int:pk>/', views.editar_plan_view, name='editar-plan'),
    path('planes/detalle/<int:pk>/', views.detalle_plan_view, name='plan-detalle'),
    path('planes/eliminar/<int:pk>/', views.eliminar_plan_view, name='eliminar-plan'),
    path('planes/completar/<int:pk>/', views.completar_mantenimiento_view, name='completar-mantenimiento'),
    
    # Órdenes de Trabajo
    path('ordenes/', views.ordenes_trabajo_view, name='ordenes-trabajo'),
    path('ordenes/crear/', views.crear_orden_view, name='crear-orden'),
    path('ordenes/detalle/<int:pk>/', views.detalle_orden_view, name='orden-detalle'),
    path('ordenes/actualizar/<int:pk>/', views.actualizar_orden_view, name='actualizar-orden'),
    
    # Tareas
    path('tareas/', views.tareas_view, name='tareas'),
    path('tareas/crear/<int:plan_pk>/', views.crear_tarea_view, name='crear-tarea'),
    
    # Análisis Predictivo
    path('analisis-predictivo/', views.analisis_predictivo_view, name='analisis-predictivo'),
    
    # API para tareas pendientes
    path('api/tareas-pendientes/', views.tareas_pendientes_api, name='api-tareas-pendientes'),
]