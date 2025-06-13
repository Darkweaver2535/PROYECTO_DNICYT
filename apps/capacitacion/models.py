import os
import mimetypes
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import URLValidator, FileExtensionValidator
from django.utils import timezone
from django.utils.text import slugify
from datetime import timedelta
import re

class CategoriaCapacitacion(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    color_hex = models.CharField(max_length=7, default='#3b82f6', help_text='Color en formato hexadecimal (#RRGGBB)')
    icono = models.CharField(max_length=50, default='bi-mortarboard', help_text='Clase de icono Bootstrap Icons')
    orden = models.PositiveIntegerField(default=0, help_text='Orden de visualización')
    activo = models.BooleanField(default=True)
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Categoría de Capacitación'
        verbose_name_plural = 'Categorías de Capacitación'
        ordering = ['orden', 'nombre']
    
    def __str__(self):
        return self.nombre

class DocumentoTecnico(models.Model):
    TIPO_CHOICES = [
        ('manual', 'Manual de Operación'),
        ('procedimiento', 'Procedimiento de Seguridad'),
        ('especificacion', 'Especificación Técnica'),
        ('guia', 'Guía de Mantenimiento'),
        ('normativa', 'Normativa/Reglamento'),
        ('ficha', 'Ficha Técnica'),
        ('catalogo', 'Catálogo de Productos'),
        ('instructivo', 'Instructivo'),
        ('reporte', 'Reporte Técnico'),
        ('protocolo', 'Protocolo de Seguridad'),
    ]
    
    FORMATO_CHOICES = [
        ('pdf', 'PDF'),
        ('docx', 'Word (.docx)'),
        ('xlsx', 'Excel (.xlsx)'),
        ('pptx', 'PowerPoint (.pptx)'),
        ('txt', 'Texto (.txt)'),
        ('dwg', 'AutoCAD (.dwg)'),
        ('zip', 'Archivo Comprimido (.zip)'),
    ]
    
    DIFICULTAD_CHOICES = [
        ('basico', 'Básico'),
        ('intermedio', 'Intermedio'),
        ('avanzado', 'Avanzado'),
        ('experto', 'Experto'),
    ]
    
    ESTADO_CHOICES = [
        ('borrador', 'Borrador'),
        ('revision', 'En Revisión'),
        ('publicado', 'Publicado'),
        ('obsoleto', 'Obsoleto'),
        ('archivado', 'Archivado'),
    ]
    
    CONFIDENCIALIDAD_CHOICES = [
        ('publico', 'Público'),
        ('interno', 'Uso Interno'),
        ('confidencial', 'Confidencial'),
        ('restringido', 'Acceso Restringido'),
    ]
    
    # Información básica
    titulo = models.CharField('Título', max_length=200)
    descripcion = models.TextField('Descripción')
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    
    tipo = models.CharField('Tipo de Documento', max_length=20, choices=TIPO_CHOICES, default='manual')
    categoria = models.ForeignKey(
        CategoriaCapacitacion, 
        on_delete=models.CASCADE, 
        related_name='documentos_tecnicos',
        verbose_name='Categoría'
    )
    
    # Archivos y recursos
    archivo_principal = models.FileField(
        'Archivo Principal',
        upload_to='documentos_tecnicos/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx', 'xlsx', 'pptx', 'txt', 'dwg', 'zip'])],
        blank=True, null=True,
        help_text='Archivo principal del documento'
    )
    
    formato = models.CharField('Formato', max_length=10, choices=FORMATO_CHOICES, default='pdf')
    tamaño_archivo = models.PositiveIntegerField('Tamaño (KB)', default=0, blank=True)
    
    # Contenido adicional
    contenido_html = models.TextField('Contenido HTML', blank=True, help_text='Contenido renderizable en web')
    resumen_ejecutivo = models.TextField('Resumen Ejecutivo', blank=True)
    palabras_clave = models.TextField('Palabras Clave', blank=True, help_text='Separadas por comas')
    
    # Información técnica
    autor_documento = models.CharField('Autor del Documento', max_length=200)
    revisor = models.CharField('Revisor/Aprobador', max_length=200, blank=True)
    version = models.CharField('Versión', max_length=20, default='1.0')
    codigo_documento = models.CharField('Código de Documento', max_length=50, unique=True, blank=True)
    
    # Clasificación
    dificultad = models.CharField('Nivel de Complejidad', max_length=20, choices=DIFICULTAD_CHOICES, default='basico')
    confidencialidad = models.CharField('Nivel de Confidencialidad', max_length=20, choices=CONFIDENCIALIDAD_CHOICES, default='interno')
    
    # Fechas importantes
    fecha_creacion_documento = models.DateField('Fecha de Creación del Documento', blank=True, null=True)
    fecha_revision = models.DateField('Fecha de Última Revisión', blank=True, null=True)
    fecha_vencimiento = models.DateField('Fecha de Vencimiento', blank=True, null=True, help_text='Cuándo debe revisarse')
    
    # Control y seguimiento
    estado = models.CharField('Estado', max_length=20, choices=ESTADO_CHOICES, default='borrador')
    requiere_actualizacion = models.BooleanField('Requiere Actualización', default=False)
    es_obligatorio = models.BooleanField('Lectura Obligatoria', default=False)
    
    # Objetivos y aplicación
    objetivos = models.TextField('Objetivos', blank=True, help_text='Uno por línea')
    aplicacion = models.TextField('Área de Aplicación', blank=True, help_text='Dónde se aplica este documento')
    prerequisitos = models.TextField('Prerequisitos', blank=True, help_text='Uno por línea')
    
    # Relacionamiento
    documentos_relacionados = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        verbose_name='Documentos Relacionados'
    )
    
    # Metadatos del sistema
    autor_sistema = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='documentos_tecnicos_creados',
        verbose_name='Creado por'
    )
    
    # Timestamps
    fecha_creacion = models.DateTimeField('Fecha de Creación en Sistema', auto_now_add=True)
    fecha_modificacion = models.DateTimeField('Última Modificación', auto_now=True)
    fecha_publicacion = models.DateTimeField('Fecha de Publicación', blank=True, null=True)
    
    # Estadísticas
    vistas = models.PositiveIntegerField('Visualizaciones', default=0)
    descargas = models.PositiveIntegerField('Descargas', default=0)
    valoracion_promedio = models.DecimalField('Valoración Promedio', max_digits=3, decimal_places=2, default=0.00)
    
    class Meta:
        verbose_name = 'Documento Técnico'
        verbose_name_plural = 'Documentos Técnicos'
        ordering = ['-fecha_modificacion']
        indexes = [
            models.Index(fields=['estado', 'categoria']),
            models.Index(fields=['tipo', 'confidencialidad']),
            models.Index(fields=['-fecha_modificacion']),
            models.Index(fields=['codigo_documento']),
        ]
    
    def __str__(self):
        return f"{self.get_tipo_display()}: {self.titulo} (v{self.version})"
    
    def save(self, *args, **kwargs):
        # Generar slug automáticamente
        if not self.slug:
            self.slug = slugify(self.titulo)
            # Asegurar que sea único
            counter = 1
            original_slug = self.slug
            while DocumentoTecnico.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        
        # Generar código de documento si no existe
        if not self.codigo_documento:
            # Formato: TIPO-CAT-YYYYMM-NNNN
            fecha = timezone.now()
            tipo_codigo = self.tipo[:3].upper()
            cat_codigo = self.categoria.nombre[:3].upper() if self.categoria else 'GEN'
            fecha_codigo = fecha.strftime('%Y%m')
            
            # Buscar el siguiente número secuencial
            prefix = f"{tipo_codigo}-{cat_codigo}-{fecha_codigo}"
            last_doc = DocumentoTecnico.objects.filter(
                codigo_documento__startswith=prefix
            ).order_by('-codigo_documento').first()
            
            if last_doc and last_doc.codigo_documento:
                try:
                    last_num = int(last_doc.codigo_documento.split('-')[-1])
                    next_num = last_num + 1
                except (ValueError, IndexError):
                    next_num = 1
            else:
                next_num = 1
            
            self.codigo_documento = f"{prefix}-{next_num:04d}"
        
        # Calcular tamaño del archivo
        if self.archivo_principal and hasattr(self.archivo_principal, 'size'):
            self.tamaño_archivo = self.archivo_principal.size // 1024  # Convertir a KB
        
        # Establecer fecha de publicación
        if self.estado == 'publicado' and not self.fecha_publicacion:
            self.fecha_publicacion = timezone.now()
        
        super().save(*args, **kwargs)
    
    def puede_descargar(self, usuario):
        """Verifica si el usuario puede descargar este documento según su confidencialidad"""
        if not usuario.is_authenticated:
            return False
        
        # Superusuarios pueden descargar todo
        if usuario.is_superuser:
            return True
        
        # Obtener el perfil del usuario
        try:
            perfil = usuario.perfil
        except:
            return False
        
        # Verificar según nivel de confidencialidad
        if self.confidencialidad == 'publico':
            return True
        elif self.confidencialidad == 'interno':
            return True  # Todos los usuarios internos pueden acceder
        elif self.confidencialidad == 'confidencial':
            return perfil.rol_sistema == 'administrador' or usuario.is_staff
        elif self.confidencialidad == 'restringido':
            return usuario.is_superuser
        
        return False
    
    def puede_editar(self, usuario):
        """Verifica si el usuario puede editar este documento"""
        if not usuario.is_authenticated:
            return False
        
        # Superusuarios pueden editar todo
        if usuario.is_superuser:
            return True
        
        # El autor puede editar sus propios documentos
        if self.autor_sistema == usuario:
            return True
        
        # Administradores pueden editar todo
        try:
            return usuario.perfil.rol_sistema == 'administrador'
        except:
            return False
    
    def puede_eliminar(self, usuario):
        """Verifica si el usuario puede eliminar este documento"""
        if not usuario.is_authenticated:
            return False
        
        # Solo superusuarios y administradores pueden eliminar
        if usuario.is_superuser:
            return True
        
        try:
            return usuario.perfil.rol_sistema == 'administrador'
        except:
            return False
    
    @property
    def tamaño_formateado(self):
        """Retorna el tamaño del archivo en formato legible"""
        if not self.tamaño_archivo:
            return "Tamaño desconocido"
        
        if self.tamaño_archivo < 1024:  # Menos de 1 MB
            return f"{self.tamaño_archivo} KB"
        elif self.tamaño_archivo < 1024 * 1024:  # Menos de 1 GB
            mb = self.tamaño_archivo / 1024
            return f"{mb:.1f} MB"
        else:
            gb = self.tamaño_archivo / (1024 * 1024)
            return f"{gb:.1f} GB"
    
    @property
    def objetivos_lista(self):
        """Retorna objetivos como lista"""
        if not self.objetivos:
            return []
        return [obj.strip() for obj in self.objetivos.split('\n') if obj.strip()]
    
    @property
    def prerequisitos_lista(self):
        """Retorna prerequisitos como lista"""
        if not self.prerequisitos:
            return []
        return [req.strip() for req in self.prerequisitos.split('\n') if req.strip()]
    
    @property
    def palabras_clave_lista(self):
        """Retorna palabras clave como lista"""
        if not self.palabras_clave:
            return []
        return [palabra.strip() for palabra in self.palabras_clave.split(',') if palabra.strip()]
    
    @property
    def esta_vigente(self):
        """Verifica si el documento está vigente"""
        if not self.fecha_vencimiento:
            return True
        return self.fecha_vencimiento >= timezone.now().date()
    
    @property
    def dias_para_vencer(self):
        """Retorna días para vencer o None si no hay fecha de vencimiento"""
        if not self.fecha_vencimiento:
            return None
        delta = self.fecha_vencimiento - timezone.now().date()
        return delta.days
    
    @property
    def icono_tipo(self):
        """Retorna el icono Bootstrap correspondiente al tipo"""
        iconos = {
            'manual': 'bi-book',
            'procedimiento': 'bi-list-check',
            'especificacion': 'bi-file-text',
            'guia': 'bi-compass',
            'normativa': 'bi-shield-check',
            'ficha': 'bi-card-text',
            'catalogo': 'bi-grid-3x3',
            'instructivo': 'bi-info-circle',
            'reporte': 'bi-file-bar-graph',
            'protocolo': 'bi-shield-exclamation',
        }
        return iconos.get(self.tipo, 'bi-file-earmark')
    
    @property
    def color_estado(self):
        """Retorna el color correspondiente al estado"""
        colores = {
            'borrador': '#6b7280',
            'revision': '#f59e0b',
            'publicado': '#10b981',
            'obsoleto': '#ef4444',
            'archivado': '#64748b',
        }
        return colores.get(self.estado, '#6b7280')
    
    @property
    def extension_archivo(self):
        """Retorna la extensión del archivo"""
        if self.archivo_principal and hasattr(self.archivo_principal, 'name'):
            return self.archivo_principal.name.split('.')[-1].upper()
        return self.formato.upper()
    
    @property
    def color_por_tipo(self):
        """Retorna color distintivo por tipo de documento"""
        colores = {
            'manual': '#8b5cf6',
            'procedimiento': '#ef4444',
            'especificacion': '#3b82f6',
            'guia': '#10b981',
            'normativa': '#f59e0b',
            'ficha': '#06b6d4',
            'catalogo': '#ec4899',
            'instructivo': '#14b8a6',
            'reporte': '#64748b',
            'protocolo': '#dc2626',
        }
        return colores.get(self.tipo, '#6b7280')
    
    def get_url_descarga(self):
        """URL para descargar el documento"""
        from django.urls import reverse
        return reverse('capacitacion:descargar-documento', kwargs={'documento_id': self.id})
    
    def incrementar_vista(self, usuario):
        """Incrementa el contador de vistas y registra en historial"""
        self.vistas += 1
        self.save(update_fields=['vistas'])
        
        # Registrar en historial
        HistorialDocumento.objects.create(
            documento=self,
            usuario=usuario,
            accion='ver',
            descripcion=f'Visualización del documento: {self.titulo}',
        )
    
    def incrementar_descarga(self, usuario):
        """Incrementa el contador de descargas y registra en historial"""
        self.descargas += 1
        self.save(update_fields=['descargas'])
        
        # Registrar en historial
        HistorialDocumento.objects.create(
            documento=self,
            usuario=usuario,
            accion='descargar',
            descripcion=f'Descarga del documento: {self.titulo}',
        )
    
    def actualizar_valoracion_promedio(self):
        """Actualiza la valoración promedio basada en las valoraciones existentes"""
        valoraciones = self.valoraciones.all()
        if valoraciones.exists():
            promedio = sum([v.valoracion for v in valoraciones]) / valoraciones.count()
            self.valoracion_promedio = round(promedio, 2)
        else:
            self.valoracion_promedio = 0.00
        self.save(update_fields=['valoracion_promedio'])

class HistorialDocumento(models.Model):
    """Historial de cambios en documentos técnicos"""
    
    ACCION_CHOICES = [
        ('crear', 'Documento Creado'),
        ('editar', 'Documento Editado'),
        ('publicar', 'Documento Publicado'),
        ('archivar', 'Documento Archivado'),
        ('ver', 'Documento Visualizado'),
        ('descargar', 'Documento Descargado'),
        ('cambiar_version', 'Versión Actualizada'),
        ('cambiar_estado', 'Estado Cambiado'),
    ]
    
    documento = models.ForeignKey(
        DocumentoTecnico,
        on_delete=models.CASCADE,
        related_name='historial'
    )
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    accion = models.CharField(max_length=20, choices=ACCION_CHOICES)
    descripcion = models.TextField(blank=True)
    
    # Datos adicionales
    version_anterior = models.CharField(max_length=20, blank=True)
    version_nueva = models.CharField(max_length=20, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    fecha = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Historial de Documento'
        verbose_name_plural = 'Historial de Documentos'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.documento.titulo} - {self.get_accion_display()} por {self.usuario.username}"

class ValoracionDocumento(models.Model):
    """Valoraciones de documentos por usuarios"""
    
    documento = models.ForeignKey(
        DocumentoTecnico,
        on_delete=models.CASCADE,
        related_name='valoraciones'
    )
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    valoracion = models.PositiveIntegerField(
        choices=[(i, i) for i in range(1, 6)],
        help_text='Valoración del 1 al 5'
    )
    comentario = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Valoración de Documento'
        verbose_name_plural = 'Valoraciones de Documentos'
        unique_together = ['documento', 'usuario']
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.documento.titulo} - {self.valoracion}★ por {self.usuario.username}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Actualizar valoración promedio del documento
        self.documento.actualizar_valoracion_promedio()

# Mantener el resto de modelos existentes (CursoTaller, etc.)
class CursoTaller(models.Model):
    TIPO_CHOICES = [
        ('curso', 'Curso'),
        ('taller', 'Taller'),
        ('conferencia', 'Conferencia'),
        ('seminario', 'Seminario'),
    ]
    
    DIFICULTAD_CHOICES = [
        ('basico', 'Básico'),
        ('intermedio', 'Intermedio'),
        ('avanzado', 'Avanzado'),
    ]
    
    MODALIDAD_CHOICES = [
        ('presencial', 'Presencial'),
        ('virtual', 'Virtual'),
        ('hibrido', 'Híbrido'),
    ]
    
    ESTADO_CHOICES = [
        ('borrador', 'Borrador'),
        ('publicado', 'Publicado'),
        ('archivado', 'Archivado'),
    ]
    
    # Información básica
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='curso')
    categoria = models.ForeignKey(CategoriaCapacitacion, on_delete=models.CASCADE, related_name='cursos')
    
    # Detalles del contenido
    instructor = models.CharField(max_length=200)
    duracion_horas = models.PositiveIntegerField(help_text='Duración estimada en horas')
    duracion_minutos = models.PositiveIntegerField(default=0, help_text='Minutos adicionales')
    dificultad = models.CharField(max_length=20, choices=DIFICULTAD_CHOICES, default='basico')
    modalidad = models.CharField(max_length=20, choices=MODALIDAD_CHOICES, default='virtual')
    
    # Enlaces y recursos
    enlace_youtube = models.URLField(
        validators=[URLValidator()],
        help_text='URL del video de YouTube (ej: https://www.youtube.com/watch?v=VIDEO_ID)'
    )
    youtube_video_id = models.CharField(max_length=50, blank=True, help_text='ID del video de YouTube (se extrae automáticamente)')
    
    # Información adicional
    objetivos = models.TextField(blank=True, help_text='Objetivos de aprendizaje (uno por línea)')
    requisitos = models.TextField(blank=True, help_text='Requisitos previos (uno por línea)')
    contenido_temas = models.TextField(blank=True, help_text='Temas que se cubren (uno por línea)')
    
    # Fechas y programación
    fecha_programada = models.DateTimeField(blank=True, null=True, help_text='Fecha programada para cursos presenciales')
    fecha_limite_inscripcion = models.DateTimeField(blank=True, null=True)
    
    # Configuración
    max_participantes = models.PositiveIntegerField(default=0, help_text='0 = Sin límite')
    certificacion_disponible = models.BooleanField(default=False)
    puntos_capacitacion = models.PositiveIntegerField(default=1, help_text='Puntos que otorga este curso')
    
    # Control
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='borrador')
    destacado = models.BooleanField(default=False, help_text='Mostrar en sección destacados')
    
    # Metadatos
    etiquetas = models.TextField(blank=True, help_text='Etiquetas separadas por comas')
    autor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='cursos_creados')
    
    # Timestamps
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    fecha_publicacion = models.DateTimeField(blank=True, null=True)
    
    # Estadísticas
    vistas = models.PositiveIntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'Curso/Taller'
        verbose_name_plural = 'Cursos/Talleres'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['estado', 'categoria']),
            models.Index(fields=['fecha_programada']),
            models.Index(fields=['-fecha_creacion']),
        ]
    
    def __str__(self):
        return f"{self.get_tipo_display()}: {self.titulo}"
    
    def save(self, *args, **kwargs):
        # Extraer ID del video de YouTube
        if self.enlace_youtube:
            self.youtube_video_id = self.extraer_youtube_id()
        
        # Establecer fecha de publicación
        if self.estado == 'publicado' and not self.fecha_publicacion:
            self.fecha_publicacion = timezone.now()
        
        super().save(*args, **kwargs)
    
    def extraer_youtube_id(self):
        """Extrae el ID del video de YouTube desde diferentes formatos de URL"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/watch\?.*v=([^&\n?#]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.enlace_youtube)
            if match:
                return match.group(1)
        return ''
    
    @property
    def duracion_total_minutos(self):
        return (self.duracion_horas * 60) + self.duracion_minutos
    
    @property
    def duracion_formateada(self):
        if self.duracion_minutos > 0:
            return f"{self.duracion_horas}h {self.duracion_minutos}m"
        return f"{self.duracion_horas}h"
    
    @property
    def youtube_thumbnail_url(self):
        if self.youtube_video_id:
            return f"https://img.youtube.com/vi/{self.youtube_video_id}/maxresdefault.jpg"
        return None
    
    @property
    def youtube_embed_url(self):
        if self.youtube_video_id:
            return f"https://www.youtube.com/embed/{self.youtube_video_id}"
        return None
    
    @property
    def objetivos_lista(self):
        if not self.objetivos:
            return []
        return [obj.strip() for obj in self.objetivos.split('\n') if obj.strip()]
    
    @property
    def requisitos_lista(self):
        if not self.requisitos:
            return []
        return [req.strip() for req in self.requisitos.split('\n') if req.strip()]
    
    @property
    def contenido_lista(self):
        if not self.contenido_temas:
            return []
        return [tema.strip() for tema in self.contenido_temas.split('\n') if tema.strip()]
    
    @property
    def etiquetas_lista(self):
        if not self.etiquetas:
            return []
        return [tag.strip() for tag in self.etiquetas.split(',') if tag.strip()]

class InscripcionCurso(models.Model):
    ESTADO_CHOICES = [
        ('inscrito', 'Inscrito'),
        ('en_progreso', 'En Progreso'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    ]
    
    curso = models.ForeignKey(CursoTaller, on_delete=models.CASCADE, related_name='inscripciones')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inscripciones_cursos')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='inscrito')
    
    # Progreso
    progreso_porcentaje = models.PositiveIntegerField(default=0, help_text='Porcentaje de progreso (0-100)')
    fecha_inicio = models.DateTimeField(blank=True, null=True)
    fecha_completado = models.DateTimeField(blank=True, null=True)
    
    # Calificación y feedback
    calificacion = models.PositiveIntegerField(blank=True, null=True, help_text='Calificación del 1 al 5')
    comentario = models.TextField(blank=True)
    
    # Control
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)
    ultima_actividad = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Inscripción a Curso'
        verbose_name_plural = 'Inscripciones a Cursos'
        unique_together = ['curso', 'usuario']
        ordering = ['-fecha_inscripcion']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.curso.titulo}"

class HistorialVisualizacion(models.Model):
    curso = models.ForeignKey(CursoTaller, on_delete=models.CASCADE, related_name='visualizaciones')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='visualizaciones')
    fecha_visualizacion = models.DateTimeField(auto_now_add=True)
    tiempo_visualizado = models.PositiveIntegerField(default=0, help_text='Tiempo en segundos')
    
    class Meta:
        verbose_name = 'Historial de Visualización'
        verbose_name_plural = 'Historial de Visualizaciones'
        ordering = ['-fecha_visualizacion']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.curso.titulo} - {self.fecha_visualizacion}"

# Funciones auxiliares para DocumentoTecnico
def documento_upload_path(instance, filename):
    """Función para definir la ruta de subida de documentos"""
    from django.utils.text import slugify
    
    # Obtener extensión del archivo
    ext = filename.split('.')[-1]
    
    # Crear nombre basado en el título y timestamp
    nombre_base = slugify(instance.titulo)[:50]
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    nuevo_nombre = f"{nombre_base}_{timestamp}.{ext}"
    
    return f'documentos_tecnicos/{instance.tipo}/{nuevo_nombre}'
