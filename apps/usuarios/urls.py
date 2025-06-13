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
    
    # Roles y permisos - Vista principal
    path('roles-permisos/', views.roles_permisos_view, name='roles-permisos'),
    
    # Vista para ver permisos detallados
    path('roles/<str:rol_id>/permisos/', views.ver_permisos_rol_view, name='ver-permisos-rol'),
    
    # Gestión de roles personalizados
    path('roles/crear/', views.crear_rol_view, name='crear-rol'),
    path('roles/editar/<int:rol_id>/', views.editar_rol_view, name='editar-rol'),
    path('roles/eliminar/<int:rol_id>/', views.eliminar_rol_view, name='eliminar-rol'),
    path('roles/asignar/', views.asignar_rol_view, name='asignar-rol'),
    
    # Gestión de permisos
    path('permisos/', views.gestionar_permisos_view, name='gestionar-permisos'),
    
    # Historial y auditoría
    path('historial-roles/', views.historial_roles_view, name='historial-roles'),
    
    # ✅ GESTIÓN DE RESPALDOS
    path('respaldos/', views.respaldos_view, name='respaldos'),
    path('respaldos/crear/', views.crear_respaldo_view, name='crear-respaldo'),
    path('respaldos/descargar/<str:nombre_archivo>/', views.descargar_respaldo_view, name='descargar-respaldo'),
    path('respaldos/eliminar/<str:nombre_archivo>/', views.eliminar_respaldo_view, name='eliminar-respaldo'),
    
    # APIs
    path('api/stats/', views.api_usuarios_stats, name='api-stats'),
]