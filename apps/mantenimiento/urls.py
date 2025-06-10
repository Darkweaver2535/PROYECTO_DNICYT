from django.urls import path
from . import views

app_name = 'mantenimiento'

urlpatterns = [
    # Planes de mantenimiento
    path('', views.planes_mantenimiento_view, name='planes-mantenimiento'),
    path('crear/', views.crear_plan_view, name='crear-plan'),
    path('plan/<int:pk>/', views.detalle_plan_view, name='plan-detalle'),
    path('plan/<int:pk>/editar/', views.editar_plan_view, name='editar-plan'),
    path('plan/<int:pk>/eliminar/', views.eliminar_plan_view, name='eliminar-plan'),
    
    # Tareas de mantenimiento
    path('tareas/', views.tareas_view, name='tareas'),
    path('plan/<int:plan_pk>/crear-tarea/', views.crear_tarea_view, name='crear-tarea'),
]