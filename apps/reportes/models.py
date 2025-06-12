from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.equipos.models import Equipo
from apps.materiales.models import Material
from datetime import date, timedelta

class ReporteGenerado(models.Model):
    """Modelo para rastrear reportes generados"""
    
    TIPO_REPORTE_CHOICES = [
        ('equipos_general', 'Reporte General de Equipos'),
        ('equipos_estado', 'Reporte por Estado de Equipos'),
        ('equipos_mantenimiento', 'Reporte de Mantenimiento'),
        ('equipos_ubicacion', 'Reporte por Ubicación'),
        ('equipos_criticidad', 'Reporte por Criticidad'),
        ('equipos_valor', 'Reporte de Valor de Equipos'),
        ('equipos_antiguedad', 'Reporte de Antigüedad'),
        ('materiales_stock', 'Reporte de Stock de Materiales'),
        ('materiales_movimientos', 'Reporte de Movimientos'),
        ('herramientas_calibracion', 'Reporte de Calibración'),
        ('analisis_fallas', 'Análisis de Fallas'),
    ]
    
    FORMATO_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
    ]
    
    titulo = models.CharField("Título del Reporte", max_length=200)
    tipo_reporte = models.CharField("Tipo de Reporte", max_length=30, choices=TIPO_REPORTE_CHOICES)
    formato = models.CharField("Formato", max_length=10, choices=FORMATO_CHOICES)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reportes_generados')
    fecha_generacion = models.DateTimeField("Fecha de Generación", auto_now_add=True)
    parametros_filtros = models.JSONField("Parámetros de Filtros", default=dict, blank=True)
    total_registros = models.PositiveIntegerField("Total de Registros", default=0)
    archivo_generado = models.FileField("Archivo Generado", upload_to='reportes/', blank=True, null=True)
    tiempo_generacion = models.DecimalField("Tiempo de Generación (segundos)", max_digits=6, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = "Reporte Generado"
        verbose_name_plural = "Reportes Generados"
        ordering = ['-fecha_generacion']
    
    def __str__(self):
        return f"{self.titulo} - {self.get_formato_display()} - {self.fecha_generacion.strftime('%d/%m/%Y')}"

class AnalisisEquipos(models.Model):
    """Modelo para análisis automatizados de equipos"""
    
    fecha_analisis = models.DateTimeField("Fecha de Análisis", auto_now_add=True)
    total_equipos = models.PositiveIntegerField("Total de Equipos", default=0)
    equipos_operativos = models.PositiveIntegerField("Equipos Operativos", default=0)
    equipos_mantenimiento = models.PositiveIntegerField("Equipos en Mantenimiento", default=0)
    equipos_fuera_servicio = models.PositiveIntegerField("Equipos Fuera de Servicio", default=0)
    disponibilidad_promedio = models.DecimalField("Disponibilidad Promedio (%)", max_digits=5, decimal_places=2, default=0)
    tiempo_promedio_mantenimiento = models.DecimalField("Tiempo Promedio Mantenimiento (horas)", max_digits=8, decimal_places=2, default=0)
    costo_mantenimiento_estimado = models.DecimalField("Costo Mantenimiento Estimado", max_digits=12, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = "Análisis de Equipos"
        verbose_name_plural = "Análisis de Equipos"
        ordering = ['-fecha_analisis']
    
    def __str__(self):
        return f"Análisis {self.fecha_analisis.strftime('%d/%m/%Y %H:%M')}"

class RegistroFalla(models.Model):
    """Modelo principal para el registro de fallas de equipos"""
    
    SEVERIDAD_CHOICES = [
        ('critica', 'Crítica'),
        ('alta', 'Alta'),
        ('media', 'Media'),
        ('baja', 'Baja'),
    ]
    
    ESTADO_CHOICES = [
        ('identificada', 'Identificada'),
        ('analisis', 'En Análisis'),
        ('solucionada', 'Solucionada'),
        ('pendiente', 'Pendiente'),
        ('cerrada', 'Cerrada'),
    ]
    
    TIPO_FALLA_CHOICES = [
        ('mecanica', 'Mecánica'),
        ('electrica', 'Eléctrica'),
        ('hidraulica', 'Hidráulica'),
        ('neumatica', 'Neumática'),
        ('software', 'Software'),
        ('operacional', 'Operacional'),
        ('desgaste', 'Desgaste Natural'),
        ('calibracion', 'Descalibración'),
        ('contaminacion', 'Contaminación'),
        ('sobrecarga', 'Sobrecarga'),
        ('vibracion', 'Vibración Excesiva'),
        ('temperatura', 'Problema Térmico'),
    ]
    
    CAUSA_RAIZ_CHOICES = [
        ('mantenimiento_inadecuado', 'Mantenimiento Inadecuado'),
        ('desgaste_natural', 'Desgaste Natural'),
        ('operacion_incorrecta', 'Operación Incorrecta'),
        ('sobrecarga_equipo', 'Sobrecarga del Equipo'),
        ('falta_lubricacion', 'Falta de Lubricación'),
        ('contaminacion_ambiente', 'Contaminación Ambiental'),
        ('defecto_fabricacion', 'Defecto de Fabricación'),
        ('instalacion_incorrecta', 'Instalación Incorrecta'),
        ('falta_capacitacion', 'Falta de Capacitación'),
        ('componente_defectuoso', 'Componente Defectuoso'),
        ('condiciones_ambientales', 'Condiciones Ambientales Adversas'),
        ('fatiga_material', 'Fatiga del Material'),
        ('corrosion', 'Corrosión'),
        ('interferencia_electromagnetica', 'Interferencia Electromagnética'),
        ('desconocida', 'Causa Desconocida'),
    ]
    
    # Información básica
    codigo_falla = models.CharField("Código de Falla", max_length=20, unique=True)
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='fallas_registradas')
    descripcion_falla = models.TextField("Descripción de la Falla")
    fecha_ocurrencia = models.DateTimeField("Fecha de Ocurrencia")
    fecha_registro = models.DateTimeField("Fecha de Registro", auto_now_add=True)
    
    # Clasificación
    severidad = models.CharField("Severidad", max_length=10, choices=SEVERIDAD_CHOICES)
    estado = models.CharField("Estado", max_length=15, choices=ESTADO_CHOICES, default='identificada')
    tipo_falla = models.CharField("Tipo de Falla", max_length=20, choices=TIPO_FALLA_CHOICES)
    
    # Análisis de causa
    causa_raiz = models.CharField("Causa Raíz", max_length=30, choices=CAUSA_RAIZ_CHOICES, blank=True, null=True)
    causa_inmediata = models.TextField("Causa Inmediata", blank=True, null=True)
    condiciones_operacion = models.TextField("Condiciones de Operación", blank=True, null=True)
    
    # Impacto
    tiempo_parada = models.DecimalField("Tiempo de Parada (horas)", max_digits=8, decimal_places=2, blank=True, null=True)
    costo_reparacion = models.DecimalField("Costo de Reparación", max_digits=12, decimal_places=2, blank=True, null=True)
    produccion_perdida = models.DecimalField("Producción Perdida", max_digits=12, decimal_places=2, blank=True, null=True)
    indice_criticidad = models.IntegerField("Índice de Criticidad", validators=[MinValueValidator(1), MaxValueValidator(100)], default=50)
    
    # Personal involucrado
    reportado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='fallas_reportadas')
    asignado_a = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='fallas_asignadas')
    supervisor = models.CharField("Supervisor", max_length=100, blank=True, null=True)
    
    # Solución
    solucion_aplicada = models.TextField("Solución Aplicada", blank=True, null=True)
    fecha_solucion = models.DateTimeField("Fecha de Solución", blank=True, null=True)
    tiempo_reparacion = models.DecimalField("Tiempo de Reparación (horas)", max_digits=6, decimal_places=2, blank=True, null=True)
    repuestos_utilizados = models.TextField("Repuestos Utilizados", blank=True, null=True)
    
    # Prevención
    acciones_preventivas = models.TextField("Acciones Preventivas", blank=True, null=True)
    recomendaciones = models.TextField("Recomendaciones", blank=True, null=True)
    
    # Documentos
    foto_falla = models.ImageField("Foto de la Falla", upload_to='fallas/fotos/', blank=True, null=True)
    reporte_tecnico = models.FileField("Reporte Técnico", upload_to='fallas/reportes/', blank=True, null=True)
    
    # Control
    requiere_seguimiento = models.BooleanField("Requiere Seguimiento", default=False)
    fecha_seguimiento = models.DateField("Fecha de Seguimiento", blank=True, null=True)
    observaciones = models.TextField("Observaciones", blank=True, null=True)
    activo = models.BooleanField("Activo", default=True)
    fecha_actualizacion = models.DateTimeField("Última Actualización", auto_now=True)
    
    class Meta:
        verbose_name = "Registro de Falla"
        verbose_name_plural = "Registros de Fallas"
        ordering = ['-fecha_ocurrencia']
    
    def __str__(self):
        return f"{self.codigo_falla} - {self.equipo.nombre}"
    
    def save(self, *args, **kwargs):
        # Generar código automático si no existe
        if not self.codigo_falla:
            ultimo_registro = RegistroFalla.objects.filter(
                codigo_falla__startswith='FLL'
            ).order_by('codigo_falla').last()
            
            if ultimo_registro:
                try:
                    ultimo_numero = int(ultimo_registro.codigo_falla.split('-')[1])
                    nuevo_numero = ultimo_numero + 1
                except (ValueError, IndexError):
                    nuevo_numero = 1
            else:
                nuevo_numero = 1
            
            self.codigo_falla = f"FLL-{nuevo_numero:04d}"
        
        # Calcular índice de criticidad automáticamente
        if not self.indice_criticidad or self.indice_criticidad == 50:
            self.calcular_indice_criticidad()
        
        super().save(*args, **kwargs)
    
    def calcular_indice_criticidad(self):
        """Calcula el índice de criticidad basado en múltiples factores"""
        criticidad = 0
        
        # Factor severidad (30%)
        severidad_pesos = {
            'critica': 30,
            'alta': 22,
            'media': 15,
            'baja': 8
        }
        criticidad += severidad_pesos.get(self.severidad, 15)
        
        # Factor tiempo de parada (25%)
        if self.tiempo_parada:
            if self.tiempo_parada >= 24:
                criticidad += 25
            elif self.tiempo_parada >= 8:
                criticidad += 18
            elif self.tiempo_parada >= 2:
                criticidad += 12
            else:
                criticidad += 6
        
        # Factor costo (20%)
        if self.costo_reparacion:
            if self.costo_reparacion >= 10000:
                criticidad += 20
            elif self.costo_reparacion >= 5000:
                criticidad += 15
            elif self.costo_reparacion >= 1000:
                criticidad += 10
            else:
                criticidad += 5
        
        # Factor recurrencia (15%)
        fallas_similares = RegistroFalla.objects.filter(
            equipo=self.equipo,
            tipo_falla=self.tipo_falla,
            fecha_ocurrencia__gte=timezone.now() - timedelta(days=180)
        ).count()
        
        if fallas_similares >= 3:
            criticidad += 15
        elif fallas_similares >= 2:
            criticidad += 10
        else:
            criticidad += 5
        
        # Factor seguridad (10%)
        if self.tipo_falla in ['electrica', 'hidraulica', 'sobrecarga']:
            criticidad += 10
        else:
            criticidad += 5
        
        self.indice_criticidad = min(criticidad, 100)
    
    def get_color_severidad(self):
        """Retorna el color CSS asociado a la severidad"""
        colores = {
            'critica': '#dc2626',
            'alta': '#ea580c',
            'media': '#2563eb',
            'baja': '#16a34a',
        }
        return colores.get(self.severidad, '#6b7280')
    
    def get_dias_transcurridos(self):
        """Calcula los días transcurridos desde la ocurrencia"""
        return (timezone.now().date() - self.fecha_ocurrencia.date()).days
    
    def esta_vencida(self):
        """Determina si la falla está vencida para resolución"""
        dias_limite = {
            'critica': 1,
            'alta': 3,
            'media': 7,
            'baja': 15
        }
        
        if self.estado in ['solucionada', 'cerrada']:
            return False
        
        limite = dias_limite.get(self.severidad, 7)
        return self.get_dias_transcurridos() > limite
    
    def calcular_mttr(self):
        """Calcula el MTTR (Mean Time To Repair) si está resuelto"""
        if self.fecha_solucion and self.tiempo_reparacion:
            return self.tiempo_reparacion
        return None

class SeguimientoFalla(models.Model):
    """Modelo para seguimiento de fallas"""
    
    TIPO_ACCION_CHOICES = [
        ('diagnostico', 'Diagnóstico'),
        ('reparacion_temporal', 'Reparación Temporal'),
        ('reparacion_definitiva', 'Reparación Definitiva'),
        ('reemplazo_componente', 'Reemplazo de Componente'),
        ('ajuste_parametros', 'Ajuste de Parámetros'),
        ('prueba_funcionamiento', 'Prueba de Funcionamiento'),
        ('verificacion_solucion', 'Verificación de Solución'),
        ('cierre_falla', 'Cierre de Falla'),
    ]
    
    falla = models.ForeignKey(RegistroFalla, on_delete=models.CASCADE, related_name='seguimientos')
    fecha_accion = models.DateTimeField("Fecha de Acción", default=timezone.now)
    tipo_accion = models.CharField("Tipo de Acción", max_length=25, choices=TIPO_ACCION_CHOICES)
    descripcion_accion = models.TextField("Descripción de la Acción")
    responsable = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    tiempo_empleado = models.DecimalField("Tiempo Empleado (horas)", max_digits=6, decimal_places=2, blank=True, null=True)
    costo_accion = models.DecimalField("Costo de la Acción", max_digits=10, decimal_places=2, blank=True, null=True)
    resultado = models.TextField("Resultado Obtenido", blank=True, null=True)
    observaciones = models.TextField("Observaciones", blank=True, null=True)
    
    class Meta:
        verbose_name = "Seguimiento de Falla"
        verbose_name_plural = "Seguimientos de Fallas"
        ordering = ['-fecha_accion']
    
    def __str__(self):
        return f"{self.falla.codigo_falla} - {self.get_tipo_accion_display()}"