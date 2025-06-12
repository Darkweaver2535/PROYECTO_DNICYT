from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import PerfilUsuario, SesionUsuario, ConfiguracionUsuario

# Extender el admin de User para incluir el perfil
class PerfilUsuarioInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = 'Perfil'
    fk_name = 'user'  # ✅ ESPECIFICAR EL CAMPO EXACTO
    fields = (
        'rol_sistema', 'area_trabajo', 'cargo', 'telefono', 
        'supervisor', 'fecha_ingreso', 'recibir_notificaciones', 
        'avatar'
    )

class UserAdmin(BaseUserAdmin):
    inlines = (PerfilUsuarioInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_rol', 'is_active', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'perfil__rol_sistema', 'perfil__area_trabajo')
    
    def get_rol(self, obj):
        try:
            return obj.perfil.get_rol_sistema_display()
        except:
            return 'Sin perfil'
    get_rol.short_description = 'Rol'

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ['user', 'rol_sistema', 'area_trabajo', 'cargo', 'activo', 'fecha_ingreso']
    list_filter = ['rol_sistema', 'area_trabajo', 'activo', 'recibir_notificaciones']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'cargo']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']

@admin.register(SesionUsuario)
class SesionUsuarioAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'fecha_inicio', 'fecha_fin', 'ip_address', 'activa'
]
    list_filter = ['activa', 'fecha_inicio']
    search_fields = ['usuario__username', 'ip_address']
    readonly_fields = ['fecha_inicio']

@admin.register(ConfiguracionUsuario)
class ConfiguracionUsuarioAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'tema', 'elementos_por_pagina', 'notificar_mantenimiento']
    list_filter = ['tema', 'notificar_mantenimiento', 'notificar_stock_bajo']
    search_fields = ['usuario__username']
