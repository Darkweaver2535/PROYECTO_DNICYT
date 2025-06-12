from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    # Administración de usuarios
    path('', views.usuarios_view, name='lista-usuarios'),
    path('crear/', views.crear_usuario_view, name='crear-usuario'),
    path('detalle/<int:pk>/', views.detalle_usuario_view, name='detalle-usuario'),
    path('editar/<int:pk>/', views.editar_usuario_view, name='editar-usuario'),
    path('eliminar/<int:pk>/', views.eliminar_usuario_view, name='eliminar-usuario'),
    
    # Gestión de contraseñas
    path('cambiar-password/<int:pk>/', views.cambiar_password_view, name='cambiar-password'),
    path('cambiar-password/', views.cambiar_password_view, name='cambiar-mi-password'),
    
    # Perfil personal
    path('mi-perfil/', views.mi_perfil_view, name='mi-perfil'),
    path('configuracion/', views.configuracion_usuario_view, name='configuracion'),
    
    # APIs
    path('api/stats/', views.api_usuarios_stats, name='api-stats'),
]