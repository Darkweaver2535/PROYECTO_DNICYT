from django.urls import path
from . import views

app_name = 'mantenimiento'

urlpatterns = [
    # Planes de Mantenimiento
    path('planes/', views.planes_mantenimiento_view, name='planes-mantenimiento'),
    path('planes/crear/', views.crear_plan_view, name='crear-plan'),
    path('planes/<int:pk>/', views.detalle_plan_view, name='plan-detalle'),
    path('planes/<int:pk>/editar/', views.editar_plan_view, name='editar-plan'),
    path('planes/<int:pk>/eliminar/', views.eliminar_plan_view, name='eliminar-plan'),
    
    # Tareas de Mantenimiento
    path('tareas/', views.tareas_view, name='tareas'),
    path('tareas/crear/<int:plan_pk>/', views.crear_tarea_view, name='crear-tarea'),
]