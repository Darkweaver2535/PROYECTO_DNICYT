from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils import timezone
from datetime import timedelta

class PerfilUsuario(models.Model):
    """Modelo extendido para usuarios del sistema"""
    
    ROL_CHOICES = [
        ('administrador', 'Administrador'),
        ('operario', 'Operario'),
    ]
    
    AREA_TRABAJO_CHOICES = [
        ('soldadura', 'Soldadura'),
        ('maquinado', 'Maquinado'),
        ('prototipado', 'Prototipado'),
        ('plasticos', 'Plásticos'),
        ('fundicion', 'Fundición'),
        ('sujecion', 'Sujeción'),
        ('transporte', 'Transporte'),
        ('administracion', 'Administración'),
        ('calidad', 'Control de Calidad'),
        ('mantenimiento', 'Mantenimiento'),
        ('almacen', 'Almacén'),
        ('seguridad', 'Seguridad Industrial'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    
    # Información del trabajo
    rol_sistema = models.CharField("Rol del Sistema", max_length=20, choices=ROL_CHOICES, default='operario')
    area_trabajo = models.CharField("Área de Trabajo", max_length=20, choices=AREA_TRABAJO_CHOICES, blank=True, null=True)
    cargo = models.CharField("Cargo/Puesto", max_length=100, blank=True, null=True)
    
    # Información de contacto
    telefono = models.CharField(
        "Teléfono", 
        max_length=15, 
        blank=True, 
        null=True,
        validators=[RegexValidator(regex=r'^\+?[0-9\-\s]{7,15}$', message='Formato de teléfono inválido')]
    )
    
    # Supervisión
    supervisor = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='supervisados',
        verbose_name="Supervisor Directo"
    )
    
    # Fechas y actividad
    fecha_ingreso = models.DateField("Fecha de Ingreso", default=timezone.now)
    ultima_actividad = models.DateTimeField("Última Actividad", null=True, blank=True)
    
    # Estado y configuración
    activo = models.BooleanField("Usuario Activo", default=True)
    recibir_notificaciones = models.BooleanField("Recibir Notificaciones", default=True)
    
    # Avatar y personalización
    avatar = models.ImageField("Avatar", upload_to='usuarios/avatars/', blank=True, null=True)
    
    # Metadatos
    fecha_creacion = models.DateTimeField("Fecha de Creación", auto_now_add=True)
    fecha_actualizacion = models.DateTimeField("Última Actualización", auto_now=True)
    
    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuarios"
        ordering = ['user__first_name', 'user__last_name']
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.get_rol_sistema_display()}"
    
    def get_nombre_completo(self):
        """Retorna el nombre completo del usuario"""
        return self.user.get_full_name() or self.user.username
    
    def get_iniciales(self):
        """Genera iniciales para el avatar"""
        if self.user.first_name and self.user.last_name:
            return f"{self.user.first_name[0]}{self.user.last_name[0]}".upper()
        return self.user.username[:2].upper()
    
    def esta_conectado_recientemente(self):
        """Verifica si el usuario se conectó en las últimas 24 horas"""
        if not self.ultima_actividad:
            return False
        return self.ultima_actividad >= timezone.now() - timedelta(hours=24)
    
    def get_color_avatar(self):
        """Genera un color consistente para el avatar basado en el ID"""
        colores = [
            '#3b82f6', '#ef4444', '#10b981', '#f59e0b', 
            '#8b5cf6', '#06b6d4', '#f97316', '#84cc16'
        ]
        return colores[self.user.id % len(colores)]
    
    def puede_administrar(self):
        """Verifica si el usuario tiene permisos de administración"""
        return self.rol_sistema == 'administrador' or self.user.is_superuser
    
    def get_permisos_area(self):
        """Retorna los permisos específicos del área"""
        permisos_base = {
            'ver_equipos': True,
            'crear_reportes': True,
            'ver_inventario': True,
        }
        
        if self.rol_sistema == 'administrador':
            permisos_base.update({
                'gestionar_usuarios': True,
                'eliminar_equipos': True,
                'configurar_sistema': True,
                'ver_todos_reportes': True,
            })
        
        return permisos_base
    
    def get_rol_sistema_display(self):
        """Obtener el display del rol del sistema"""
        return dict(self.ROL_CHOICES).get(self.rol_sistema, 'Operario')

    def save(self, *args, **kwargs):
        """Sobrescribir save para auto-asignar rol a superusuarios"""
        # Si el usuario es superusuario, asegurar que sea administrador
        if self.user.is_superuser and self.rol_sistema != 'administrador':
            self.rol_sistema = 'administrador'
        
        super().save(*args, **kwargs)

class SesionUsuario(models.Model):
    """Modelo para registrar sesiones de usuarios"""
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sesiones')
    fecha_inicio = models.DateTimeField("Inicio de Sesión", default=timezone.now)
    fecha_fin = models.DateTimeField("Fin de Sesión", null=True, blank=True)
    ip_address = models.GenericIPAddressField("Dirección IP", null=True, blank=True)
    user_agent = models.TextField("User Agent", blank=True, null=True)
    activa = models.BooleanField("Sesión Activa", default=True)
    
    class Meta:
        verbose_name = "Sesión de Usuario"
        verbose_name_plural = "Sesiones de Usuarios"
        ordering = ['-fecha_inicio']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.fecha_inicio.strftime('%d/%m/%Y %H:%M')}"
    
    def duracion_sesion(self):
        """Calcula la duración de la sesión"""
        fin = self.fecha_fin or timezone.now()
        return fin - self.fecha_inicio

class ConfiguracionUsuario(models.Model):
    """Configuraciones personalizadas del usuario"""
    
    TEMA_CHOICES = [
        ('claro', 'Tema Claro'),
        ('oscuro', 'Tema Oscuro'),
        ('auto', 'Automático'),
    ]
    
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='configuracion')
    
    # Preferencias de interfaz
    tema = models.CharField("Tema", max_length=10, choices=TEMA_CHOICES, default='claro')
    mostrar_ayuda = models.BooleanField("Mostrar Ayuda", default=True)
    elementos_por_pagina = models.IntegerField("Elementos por Página", default=10)
    
    # Notificaciones
    notificar_mantenimiento = models.BooleanField("Notificar Mantenimiento", default=True)
    notificar_stock_bajo = models.BooleanField("Notificar Stock Bajo", default=True)
    notificar_fallas = models.BooleanField("Notificar Fallas", default=True)
    
    # Dashboard personalizado
    widgets_dashboard = models.JSONField("Widgets Dashboard", default=dict, blank=True)
    
    class Meta:
        verbose_name = "Configuración de Usuario"
        verbose_name_plural = "Configuraciones de Usuario"
    
    def __str__(self):
        return f"Configuración de {self.usuario.username}"
