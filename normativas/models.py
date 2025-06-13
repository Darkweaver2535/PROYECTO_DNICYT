from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.utils.text import slugify
from datetime import timedelta
import os

class CategoriaSeguridad(models.Model):
    """Categorías para clasificar normativas y protocolos de seguridad"""
    
    nombre = models.CharField('Nombre de la Categoría', max_length=100, unique=True)
    descripcion = models.TextField('Descripción', blank=True)
    color_hex = models.CharField('Color', max_length=7, default='#dc2626', 
                                help_text='Color en formato hexadecimal para identificación visual')
    icono = models.CharField('Icono', max_length=50, default='bi-shield-exclamation',
                           help_text='Clase de icono Bootstrap Icons')
    orden = models.PositiveIntegerField('Orden de Visualización', default=0)
    es_critica = models.BooleanField('Categoría Crítica', default=False,
                                   help_text='Las categorías críticas requieren revisión frecuente')
    activo = models.BooleanField('Activo', default=True)
    
    fecha_creacion = models.DateTimeField('Fecha de Creación', auto_now_add=True)
    fecha_modificacion = models.DateTimeField('Última Modificación', auto_now=True)
    
    class Meta:
        verbose_name = 'Categoría de Seguridad'
        verbose_name_plural = 'Categorías de Seguridad'
        ordering = ['orden', 'nombre']
    
    def __str__(self):
        return self.nombre
    
    @property
    def total_normativas(self):
        return self.normativas.filter(estado='vigente').count()
    
    @property
    def color_badge(self):
        return self.color_hex

class NormativaSeguridad(models.Model):
    """Modelo principal para normativas y protocolos de seguridad industrial"""
    
    TIPO_CHOICES = [
        ('normativa', 'Normativa General'),
        ('protocolo', 'Protocolo de Seguridad'),
        ('procedimiento', 'Procedimiento de Emergencia'),
        ('instructivo', 'Instructivo de Seguridad'),
        ('reglamento', 'Reglamento Interno'),
        ('politica', 'Política de Seguridad'),
        ('manual', 'Manual de Seguridad'),
        ('checklist', 'Lista de Verificación'),
        ('epp', 'Equipos de Protección Personal'),
        ('capacitacion', 'Normativa de Capacitación'),
    ]
    
    PRIORIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('critica', 'Crítica'),
    ]
    
    ESTADO_CHOICES = [
        ('borrador', 'Borrador'),
        ('revision', 'En Revisión'),
        ('vigente', 'Vigente'),
        ('suspendida', 'Suspendida'),
        ('obsoleta', 'Obsoleta'),
        ('archivada', 'Archivada'),
    ]
    
    AMBITO_CHOICES = [
        ('general', 'General - Todo el Laboratorio'),
        ('soldadura', 'Área de Soldadura'),
        ('maquinado', 'Área de Maquinado'),
        ('fundicion', 'Área de Fundición'),
        ('plasticos', 'Área de Plásticos'),
        ('prototipado', 'Área de Prototipado'),
        ('almacen', 'Área de Almacén'),
        ('administracion', 'Área Administrativa'),
        ('mantenimiento', 'Área de Mantenimiento'),
        ('emergencias', 'Emergencias y Evacuación'),
        ('visitantes', 'Protocolo para Visitantes'),
    ]
    
    # Información básica
    codigo = models.CharField('Código de Normativa', max_length=20, unique=True, blank=True)
    titulo = models.CharField('Título', max_length=200)
    slug = models.SlugField('Slug', max_length=250, unique=True, blank=True)
    descripcion = models.TextField('Descripción')
    
    # Clasificación
    tipo = models.CharField('Tipo', max_length=20, choices=TIPO_CHOICES, default='normativa')
    categoria = models.ForeignKey(CategoriaSeguridad, on_delete=models.CASCADE, 
                                related_name='normativas', verbose_name='Categoría')
    prioridad = models.CharField('Prioridad', max_length=10, choices=PRIORIDAD_CHOICES, default='media')
    ambito_aplicacion = models.CharField('Ámbito de Aplicación', max_length=20, 
                                       choices=AMBITO_CHOICES, default='general')
    
    # Contenido
    contenido = models.TextField('Contenido Detallado', help_text='Contenido principal de la normativa')
    objetivos = models.TextField('Objetivos', blank=True, help_text='Uno por línea')
    alcance = models.TextField('Alcance y Aplicabilidad', blank=True)
    responsabilidades = models.TextField('Responsabilidades', blank=True, help_text='Responsabilidades por área/cargo')
    procedimientos = models.TextField('Procedimientos', blank=True, help_text='Pasos específicos a seguir')
    recursos_necesarios = models.TextField('Recursos Necesarios', blank=True, help_text='EPP, herramientas, etc.')
    
    # Archivos adjuntos
    archivo_principal = models.FileField('Archivo Principal', upload_to='normativas/documentos/',
                                       validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx', 'doc'])],
                                       blank=True, null=True)
    imagen_referencia = models.ImageField('Imagen de Referencia', upload_to='normativas/imagenes/',
                                        blank=True, null=True, help_text='Imagen ilustrativa o diagrama')
    
    # Autorización y aprobación
    autor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, 
                            related_name='normativas_creadas', verbose_name='Autor')
    aprobado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='normativas_aprobadas', verbose_name='Aprobado por')
    fecha_aprobacion = models.DateTimeField('Fecha de Aprobación', blank=True, null=True)
    
    # Control de versiones
    version = models.CharField('Versión', max_length=10, default='1.0')
    version_anterior = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                       verbose_name='Versión Anterior')
    motivo_actualizacion = models.TextField('Motivo de Actualización', blank=True)
    
    # Vigencia y revisión
    fecha_vigencia_inicio = models.DateField('Fecha de Inicio de Vigencia')
    fecha_vigencia_fin = models.DateField('Fecha de Fin de Vigencia', blank=True, null=True)
    frecuencia_revision = models.PositiveIntegerField('Frecuencia de Revisión (días)', default=365,
                                                    validators=[MinValueValidator(30), MaxValueValidator(1095)])
    proxima_revision = models.DateField('Próxima Revisión', blank=True, null=True)
    
    # Estado y control
    estado = models.CharField('Estado', max_length=15, choices=ESTADO_CHOICES, default='borrador')
    es_obligatoria = models.BooleanField('Cumplimiento Obligatorio', default=True)
    requiere_capacitacion = models.BooleanField('Requiere Capacitación Previa', default=False)
    requiere_evaluacion = models.BooleanField('Requiere Evaluación Periódica', default=False)
    
    # Métricas y seguimiento
    vistas = models.PositiveIntegerField('Visualizaciones', default=0)
    descargas = models.PositiveIntegerField('Descargas', default=0)
    cumplimiento_promedio = models.DecimalField('Porcentaje de Cumplimiento', max_digits=5, decimal_places=2, 
                                              default=0.00, help_text='Basado en inspecciones')
    
    # Tags y palabras clave
    palabras_clave = models.TextField('Palabras Clave', blank=True, 
                                    help_text='Separadas por comas para facilitar búsquedas')
    
    # Normativas relacionadas
    normativas_relacionadas = models.ManyToManyField('self', blank=True, symmetrical=False,
                                                   verbose_name='Normativas Relacionadas')
    
    # Timestamps
    fecha_creacion = models.DateTimeField('Fecha de Creación', auto_now_add=True)
    fecha_modificacion = models.DateTimeField('Última Modificación', auto_now=True)
    fecha_publicacion = models.DateTimeField('Fecha de Publicación', blank=True, null=True)
    
    class Meta:
        verbose_name = 'Normativa de Seguridad'
        verbose_name_plural = 'Normativas de Seguridad'
        ordering = ['-fecha_modificacion']
        indexes = [
            models.Index(fields=['estado', 'categoria']),
            models.Index(fields=['tipo', 'ambito_aplicacion']),
            models.Index(fields=['prioridad', '-fecha_modificacion']),
            models.Index(fields=['codigo']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.titulo}"
    
    def save(self, *args, **kwargs):
        # Generar slug automáticamente
        if not self.slug:
            self.slug = slugify(self.titulo)
            counter = 1
            original_slug = self.slug
            while NormativaSeguridad.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        
        # Generar código automáticamente
        if not self.codigo:
            year = timezone.now().year
            tipo_prefix = self.tipo[:3].upper()
            count = NormativaSeguridad.objects.filter(
                codigo__startswith=f"NS-{tipo_prefix}-{year}"
            ).count() + 1
            self.codigo = f"NS-{tipo_prefix}-{year}-{count:04d}"
        
        # Calcular próxima revisión
        if not self.proxima_revision and self.fecha_vigencia_inicio:
            self.proxima_revision = self.fecha_vigencia_inicio + timedelta(days=self.frecuencia_revision)
        
        # Establecer fecha de publicación
        if self.estado == 'vigente' and not self.fecha_publicacion:
            self.fecha_publicacion = timezone.now()
        
        super().save(*args, **kwargs)
    
    @property
    def esta_vigente(self):
        today = timezone.now().date()
        if self.estado != 'vigente':
            return False
        if self.fecha_vigencia_fin and self.fecha_vigencia_fin < today:
            return False
        return True
    
    @property
    def requiere_revision(self):
        if not self.proxima_revision:
            return False
        return timezone.now().date() >= self.proxima_revision
    
    @property
    def dias_para_revision(self):
        if not self.proxima_revision:
            return None
        delta = self.proxima_revision - timezone.now().date()
        return delta.days
    
    @property
    def color_prioridad(self):
        colores = {
            'baja': '#10b981',
            'media': '#f59e0b', 
            'alta': '#ef4444',
            'critica': '#7c2d12',
        }
        return colores.get(self.prioridad, '#6b7280')
    
    @property
    def icono_tipo(self):
        iconos = {
            'normativa': 'bi-file-text',
            'protocolo': 'bi-clipboard-check',
            'procedimiento': 'bi-list-ol',
            'instructivo': 'bi-info-circle',
            'reglamento': 'bi-book',
            'politica': 'bi-shield-check',
            'manual': 'bi-journal',
            'checklist': 'bi-check2-square',
            'epp': 'bi-shield',
            'capacitacion': 'bi-mortarboard',
        }
        return iconos.get(self.tipo, 'bi-file-text')
    
    @property
    def objetivos_lista(self):
        if not self.objetivos:
            return []
        return [obj.strip() for obj in self.objetivos.split('\n') if obj.strip()]
    
    @property
    def palabras_clave_lista(self):
        if not self.palabras_clave:
            return []
        return [palabra.strip() for palabra in self.palabras_clave.split(',') if palabra.strip()]
    
    def incrementar_vista(self, usuario):
        self.vistas += 1
        self.save(update_fields=['vistas'])
        
        HistorialNormativa.objects.create(
            normativa=self,
            usuario=usuario,
            accion='consultar',
            descripcion=f'Visualización de la normativa: {self.titulo}',
        )
    
    def incrementar_descarga(self, usuario):
        self.descargas += 1
        self.save(update_fields=['descargas'])
        
        HistorialNormativa.objects.create(
            normativa=self,
            usuario=usuario,
            accion='descargar',
            descripcion=f'Descarga del archivo: {self.titulo}',
        )

class InspeccionSeguridad(models.Model):
    """Inspecciones de cumplimiento de normativas de seguridad"""
    
    RESULTADO_CHOICES = [
        ('cumple', 'Cumple Totalmente'),
        ('cumple_observaciones', 'Cumple con Observaciones'),
        ('no_cumple', 'No Cumple'),
        ('no_aplica', 'No Aplica'),
    ]
    
    TIPO_INSPECCION_CHOICES = [
        ('rutinaria', 'Inspección Rutinaria'),
        ('seguimiento', 'Seguimiento de Observaciones'),
        ('sorpresa', 'Inspección Sorpresa'),
        ('auditoria', 'Auditoría de Seguridad'),
        ('incidente', 'Post-Incidente'),
    ]
    
    normativa = models.ForeignKey(NormativaSeguridad, on_delete=models.CASCADE, 
                                related_name='inspecciones')
    inspector = models.ForeignKey(User, on_delete=models.CASCADE, 
                                related_name='inspecciones_realizadas')
    
    tipo_inspeccion = models.CharField('Tipo de Inspección', max_length=15, 
                                     choices=TIPO_INSPECCION_CHOICES, default='rutinaria')
    fecha_inspeccion = models.DateTimeField('Fecha de Inspección', default=timezone.now)
    area_inspeccionada = models.CharField('Área Inspeccionada', max_length=100)
    
    resultado = models.CharField('Resultado', max_length=25, choices=RESULTADO_CHOICES)
    puntuacion = models.PositiveIntegerField('Puntuación (%)', 
                                           validators=[MinValueValidator(0), MaxValueValidator(100)])
    observaciones = models.TextField('Observaciones y Hallazgos', blank=True)
    acciones_correctivas = models.TextField('Acciones Correctivas Requeridas', blank=True)
    
    fecha_limite_correccion = models.DateField('Fecha Límite para Corrección', blank=True, null=True)
    corregido = models.BooleanField('Observaciones Corregidas', default=False)
    fecha_verificacion = models.DateField('Fecha de Verificación', blank=True, null=True)
    verificado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='verificaciones_realizadas')
    
    fotos_evidencia = models.FileField('Fotos de Evidencia', upload_to='normativas/inspecciones/',
                                     blank=True, null=True,
                                     validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'pdf'])])
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Inspección de Seguridad'
        verbose_name_plural = 'Inspecciones de Seguridad'
        ordering = ['-fecha_inspeccion']
    
    def __str__(self):
        return f"Inspección {self.normativa.codigo} - {self.fecha_inspeccion.strftime('%d/%m/%Y')}"
    
    @property
    def color_resultado(self):
        colores = {
            'cumple': '#10b981',
            'cumple_observaciones': '#f59e0b',
            'no_cumple': '#ef4444',
            'no_aplica': '#6b7280',
        }
        return colores.get(self.resultado, '#6b7280')
    
    @property
    def esta_vencida(self):
        if not self.fecha_limite_correccion or self.corregido:
            return False
        return timezone.now().date() > self.fecha_limite_correccion

class IncidenteSeguridad(models.Model):
    """Registro de incidentes relacionados con seguridad industrial"""
    
    GRAVEDAD_CHOICES = [
        ('leve', 'Leve'),
        ('moderado', 'Moderado'),
        ('grave', 'Grave'),
        ('muy_grave', 'Muy Grave'),
        ('critico', 'Crítico'),
    ]
    
    TIPO_INCIDENTE_CHOICES = [
        ('accidente', 'Accidente Laboral'),
        ('casi_accidente', 'Casi Accidente'),
        ('condicion_insegura', 'Condición Insegura'),
        ('acto_inseguro', 'Acto Inseguro'),
        ('derrame', 'Derrame de Sustancias'),
        ('incendio', 'Principio de Incendio'),
        ('falla_equipo', 'Falla de Equipo de Seguridad'),
        ('exposicion', 'Exposición a Riesgo'),
    ]
    
    ESTADO_CHOICES = [
        ('reportado', 'Reportado'),
        ('investigando', 'En Investigación'),
        ('resuelto', 'Resuelto'),
        ('cerrado', 'Cerrado'),
    ]
    
    # Información básica
    numero_incidente = models.CharField('Número de Incidente', max_length=15, unique=True, blank=True)
    fecha_incidente = models.DateTimeField('Fecha y Hora del Incidente')
    fecha_reporte = models.DateTimeField('Fecha de Reporte', auto_now_add=True)
    
    # Clasificación
    tipo_incidente = models.CharField('Tipo de Incidente', max_length=20, choices=TIPO_INCIDENTE_CHOICES)
    gravedad = models.CharField('Gravedad', max_length=10, choices=GRAVEDAD_CHOICES)
    
    # Ubicación y contexto
    area_afectada = models.CharField('Área Afectada', max_length=100)
    descripcion_lugar = models.TextField('Descripción del Lugar')
    
    # Personas involucradas
    reportado_por = models.ForeignKey(User, on_delete=models.CASCADE, 
                                    related_name='incidentes_reportados')
    personas_involucradas = models.TextField('Personas Involucradas', 
                                           help_text='Nombres y roles de personas involucradas')
    testigos = models.TextField('Testigos', blank=True, help_text='Nombres de testigos')
    
    # Descripción del incidente
    descripcion_incidente = models.TextField('Descripción Detallada del Incidente')
    causas_inmediatas = models.TextField('Causas Inmediatas', blank=True)
    causas_raiz = models.TextField('Causas Raíz', blank=True)
    
    # Normativas relacionadas
    normativas_incumplidas = models.ManyToManyField(NormativaSeguridad, blank=True,
                                                   verbose_name='Normativas Incumplidas')
    
    # Acciones tomadas
    acciones_inmediatas = models.TextField('Acciones Inmediatas Tomadas')
    acciones_correctivas = models.TextField('Acciones Correctivas', blank=True)
    acciones_preventivas = models.TextField('Acciones Preventivas', blank=True)
    
    # Seguimiento
    investigador_asignado = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                            related_name='incidentes_investigados')
    estado = models.CharField('Estado', max_length=15, choices=ESTADO_CHOICES, default='reportado')
    fecha_cierre = models.DateTimeField('Fecha de Cierre', blank=True, null=True)
    
    # Archivos adjuntos
    fotos_evidencia = models.FileField('Fotos/Videos', upload_to='normativas/incidentes/',
                                     blank=True, null=True)
    reporte_completo = models.FileField('Reporte Completo', upload_to='normativas/reportes/',
                                      blank=True, null=True,
                                      validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx'])])
    
    # Metadatos
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Incidente de Seguridad'
        verbose_name_plural = 'Incidentes de Seguridad'
        ordering = ['-fecha_incidente']
        
    def __str__(self):
        return f"Incidente {self.numero_incidente} - {self.get_tipo_incidente_display()}"
    
    def save(self, *args, **kwargs):
        if not self.numero_incidente:
            year = timezone.now().year
            month = timezone.now().month
            prefix = f"INC-{year}{month:02d}"
            
            last_incident = IncidenteSeguridad.objects.filter(
                numero_incidente__startswith=prefix
            ).order_by('-numero_incidente').first()
            
            if last_incident and last_incident.numero_incidente:
                try:
                    last_num = int(last_incident.numero_incidente.split('-')[-1])
                    next_num = last_num + 1
                except (ValueError, IndexError):
                    next_num = 1
            else:
                next_num = 1
            
            self.numero_incidente = f"{prefix}-{next_num:04d}"
        
        super().save(*args, **kwargs)
    
    @property
    def color_gravedad(self):
        colores = {
            'leve': '#10b981',
            'moderado': '#f59e0b',
            'grave': '#ef4444',
            'muy_grave': '#dc2626',
            'critico': '#7c2d12',
        }
        return colores.get(self.gravedad, '#6b7280')
    
    @property
    def dias_desde_incidente(self):
        return (timezone.now().date() - self.fecha_incidente.date()).days

class HistorialNormativa(models.Model):
    """Historial de cambios y accesos a normativas"""
    
    ACCION_CHOICES = [
        ('crear', 'Normativa Creada'),
        ('editar', 'Normativa Editada'),
        ('aprobar', 'Normativa Aprobada'),
        ('publicar', 'Normativa Publicada'),
        ('suspender', 'Normativa Suspendida'),
        ('archivar', 'Normativa Archivada'),
        ('consultar', 'Normativa Consultada'),
        ('descargar', 'Archivo Descargado'),
        ('nueva_version', 'Nueva Versión Creada'),
    ]
    
    normativa = models.ForeignKey(NormativaSeguridad, on_delete=models.CASCADE, 
                                related_name='historial')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    accion = models.CharField('Acción', max_length=15, choices=ACCION_CHOICES)
    descripcion = models.TextField('Descripción', blank=True)
    
    ip_address = models.GenericIPAddressField('Dirección IP', null=True, blank=True)
    user_agent = models.TextField('User Agent', blank=True)
    
    version_anterior = models.CharField('Versión Anterior', max_length=10, blank=True)
    version_nueva = models.CharField('Versión Nueva', max_length=10, blank=True)
    cambios_realizados = models.JSONField('Cambios Realizados', default=dict, blank=True)
    
    fecha = models.DateTimeField('Fecha', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Historial de Normativa'
        verbose_name_plural = 'Historial de Normativas'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.normativa.codigo} - {self.get_accion_display()} por {self.usuario.username}"

class CapacitacionSeguridad(models.Model):
    """Capacitaciones relacionadas con normativas de seguridad"""
    
    ESTADO_CHOICES = [
        ('programada', 'Programada'),
        ('en_curso', 'En Curso'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
        ('pospuesta', 'Pospuesta'),
    ]
    
    MODALIDAD_CHOICES = [
        ('presencial', 'Presencial'),
        ('virtual', 'Virtual'),
        ('mixta', 'Mixta'),
    ]
    
    titulo = models.CharField('Título de la Capacitación', max_length=200)
    descripcion = models.TextField('Descripción')
    
    normativas_cubiertas = models.ManyToManyField(NormativaSeguridad, 
                                                 verbose_name='Normativas Cubiertas')
    
    fecha_inicio = models.DateTimeField('Fecha de Inicio')
    fecha_fin = models.DateTimeField('Fecha de Finalización')
    modalidad = models.CharField('Modalidad', max_length=15, choices=MODALIDAD_CHOICES, default='presencial')
    lugar = models.CharField('Lugar', max_length=100, blank=True)
    
    instructor = models.CharField('Instructor/Facilitador', max_length=100)
    max_participantes = models.PositiveIntegerField('Máximo de Participantes', default=20)
    participantes = models.ManyToManyField(User, through='ParticipacionCapacitacion',
                                         verbose_name='Participantes')
    
    estado = models.CharField('Estado', max_length=15, choices=ESTADO_CHOICES, default='programada')
    es_obligatoria = models.BooleanField('Capacitación Obligatoria', default=False)
    certificacion = models.BooleanField('Otorga Certificación', default=True)
    
    material_capacitacion = models.FileField('Material de Capacitación', 
                                           upload_to='normativas/capacitaciones/',
                                           blank=True, null=True)
    
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                 related_name='capacitaciones_creadas')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Capacitación de Seguridad'
        verbose_name_plural = 'Capacitaciones de Seguridad'
        ordering = ['-fecha_inicio']
    
    def __str__(self):
        return f"{self.titulo} - {self.fecha_inicio.strftime('%d/%m/%Y')}"
    
    @property
    def participantes_inscritos(self):
        return self.participaciones.filter(estado='inscrito').count()
    
    @property
    def participantes_completaron(self):
        return self.participaciones.filter(estado='completado').count()

class ParticipacionCapacitacion(models.Model):
    """Participación de usuarios en capacitaciones de seguridad"""
    
    ESTADO_CHOICES = [
        ('inscrito', 'Inscrito'),
        ('presente', 'Presente'),
        ('ausente', 'Ausente'),
        ('completado', 'Completado'),
        ('reprobado', 'Reprobado'),
    ]
    
    capacitacion = models.ForeignKey(CapacitacionSeguridad, on_delete=models.CASCADE,
                                   related_name='participaciones')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE,
                              related_name='participaciones_seguridad')
    
    estado = models.CharField('Estado', max_length=15, choices=ESTADO_CHOICES, default='inscrito')
    fecha_inscripcion = models.DateTimeField('Fecha de Inscripción', auto_now_add=True)
    fecha_asistencia = models.DateTimeField('Fecha de Asistencia', blank=True, null=True)
    
    calificacion = models.DecimalField('Calificación', max_digits=4, decimal_places=2, 
                                     blank=True, null=True)
    aprobado = models.BooleanField('Aprobado', default=False)
    
    certificado_emitido = models.BooleanField('Certificado Emitido', default=False)
    fecha_certificacion = models.DateField('Fecha de Certificación', blank=True, null=True)
    vigencia_certificacion = models.DateField('Vigencia del Certificado', blank=True, null=True)
    
    observaciones = models.TextField('Observaciones', blank=True)
    
    class Meta:
        verbose_name = 'Participación en Capacitación'
        verbose_name_plural = 'Participaciones en Capacitaciones'
        unique_together = ['capacitacion', 'usuario']
        ordering = ['-fecha_inscripcion']
    
    def __str__(self):
        return f"{self.usuario.get_full_name()} - {self.capacitacion.titulo}"
