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
    
    # Agregar campo para rol personalizado
    rol_personalizado = models.ForeignKey(
        'RolPersonalizado', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Rol Personalizado"
    )
    
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

class PermisoSistema(models.Model):
    """Modelo para definir permisos específicos del sistema"""
    
    CATEGORIA_CHOICES = [
        ('usuarios', 'Gestión de Usuarios'),
        ('equipos', 'Gestión de Equipos'),
        ('inventario', 'Gestión de Inventario'),
        ('mantenimiento', 'Mantenimiento'),
        ('reportes', 'Reportes y Análisis'),
        ('configuracion', 'Configuración del Sistema'),
        ('seguridad', 'Seguridad Industrial'),
        ('operaciones', 'Operaciones Diarias'),
    ]
    
    codigo = models.CharField("Código del Permiso", max_length=50, unique=True)
    nombre = models.CharField("Nombre del Permiso", max_length=100)
    descripcion = models.TextField("Descripción", blank=True)
    categoria = models.CharField("Categoría", max_length=20, choices=CATEGORIA_CHOICES)
    es_critico = models.BooleanField("Permiso Crítico", default=False, help_text="No se puede desactivar")
    activo = models.BooleanField("Activo", default=True)
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Permiso del Sistema"
        verbose_name_plural = "Permisos del Sistema"
        ordering = ['categoria', 'nombre']
    
    def __str__(self):
        return f"{self.nombre} ({self.get_categoria_display()})"

class RolPersonalizado(models.Model):
    """Modelo para roles personalizados del sistema"""
    
    nombre = models.CharField("Nombre del Rol", max_length=50, unique=True)
    descripcion = models.TextField("Descripción", blank=True)
    color = models.CharField("Color", max_length=7, default="#6b7280", help_text="Color hexadecimal")
    icono = models.CharField("Icono", max_length=50, default="bi-person", help_text="Clase de Bootstrap Icon")
    
    # Permisos asignados
    permisos = models.ManyToManyField(PermisoSistema, blank=True, verbose_name="Permisos")
    
    # Configuración
    es_sistema = models.BooleanField("Rol del Sistema", default=False, help_text="No se puede eliminar")
    activo = models.BooleanField("Activo", default=True)
    
    # Metadatos
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='roles_creados')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Rol Personalizado"
        verbose_name_plural = "Roles Personalizados"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre
    
    def get_usuarios_count(self):
        """Retorna el número de usuarios con este rol"""
        return User.objects.filter(perfil__rol_personalizado=self).count()
    
    def get_permisos_por_categoria(self):
        """Retorna permisos agrupados por categoría"""
        permisos_dict = {}
        for permiso in self.permisos.filter(activo=True):
            categoria = permiso.get_categoria_display()
            if categoria not in permisos_dict:
                permisos_dict[categoria] = []
            permisos_dict[categoria].append(permiso)
        return permisos_dict

class HistorialRoles(models.Model):
    """Historial de cambios en roles y permisos"""
    
    ACCION_CHOICES = [
        ('crear_rol', 'Rol Creado'),
        ('editar_rol', 'Rol Editado'),
        ('eliminar_rol', 'Rol Eliminado'),
        ('asignar_permiso', 'Permiso Asignado'),
        ('remover_permiso', 'Permiso Removido'),
        ('cambiar_rol_usuario', 'Rol de Usuario Cambiado'),
        # ✅ AGREGAR NUEVAS ACCIONES PARA RESPALDOS
        ('crear_respaldo', 'Respaldo Creado'),
        ('descargar_respaldo', 'Respaldo Descargado'),
        ('eliminar_respaldo', 'Respaldo Eliminado'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='historial_roles')
    accion = models.CharField("Acción", max_length=20, choices=ACCION_CHOICES)
    descripcion = models.TextField("Descripción")
    
    # Referencias opcionales
    rol_afectado = models.ForeignKey(RolPersonalizado, on_delete=models.SET_NULL, null=True, blank=True)
    usuario_afectado = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='cambios_rol')
    permiso_afectado = models.ForeignKey(PermisoSistema, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Datos adicionales
    datos_antiguos = models.JSONField("Datos Anteriores", default=dict, blank=True)
    datos_nuevos = models.JSONField("Datos Nuevos", default=dict, blank=True)
    ip_address = models.GenericIPAddressField("Dirección IP", null=True, blank=True)
    
    fecha = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Historial de Roles"
        verbose_name_plural = "Historial de Roles"
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.get_accion_display()} - {self.fecha.strftime('%d/%m/%Y %H:%M')}"

    def get_permisos_efectivos(self):
        """Obtiene todos los permisos efectivos del usuario"""
        permisos = set()
        
        # Permisos por rol del sistema (compatibilidad)
        if self.rol_sistema == 'administrador':
            permisos.update([
                'gestionar_usuarios', 'configurar_sistema', 'eliminar_equipos',
                'ver_todos_reportes', 'gestionar_mantenimiento', 'gestionar_inventario',
                'eliminar_registros', 'exportar_datos'
            ])
        else:
            permisos.update([
                'ver_equipos', 'crear_reportes', 'ver_inventario',
                'registrar_operaciones', 'ver_manuales'
            ])
        
        # Permisos por rol personalizado
        if self.rol_personalizado:
            permisos.update([p.codigo for p in self.rol_personalizado.permisos.filter(activo=True)])
        
        return list(permisos)
    
    def tiene_permiso(self, codigo_permiso):
        """Verifica si el usuario tiene un permiso específico"""
        return codigo_permiso in self.get_permisos_efectivos()
