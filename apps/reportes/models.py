from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from apps.equipos.models import Equipo
from apps.materiales.models import Material

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