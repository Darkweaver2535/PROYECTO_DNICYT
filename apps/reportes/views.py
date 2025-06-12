from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.db.models import Count, Q, Avg, Sum, F, Case, When, IntegerField
from django.db.models.functions import TruncMonth, TruncWeek, ExtractYear
from django.utils import timezone
from datetime import datetime, timedelta, date
from collections import defaultdict
import json

# Importaciones para Excel
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Importaciones para PDF
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# Importar modelos
from apps.equipos.models import Equipo
from apps.materiales.models import Material, MovimientoMaterial
from apps.mantenimiento.models import PlanMantenimiento, OrdenTrabajo
from .models import ReporteGenerado, AnalisisEquipos

@login_required
def reportes_equipos_view(request):
    """Vista principal de Reportes de Equipos con análisis completo"""
    
    # Obtener filtros de la URL
    seccion_filtro = request.GET.get('seccion', '')
    estado_filtro = request.GET.get('estado', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    tipo_analisis = request.GET.get('tipo_analisis', 'general')
    
    # === CONSULTA BASE DE EQUIPOS ===
    equipos_queryset = Equipo.objects.all()
    
    # Aplicar filtros
    if seccion_filtro:
        equipos_queryset = equipos_queryset.filter(seccion=seccion_filtro)
    
    if estado_filtro:
        equipos_queryset = equipos_queryset.filter(estado=estado_filtro)
    
    if fecha_desde:
        try:
            fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
            equipos_queryset = equipos_queryset.filter(fecha_ingreso__date__gte=fecha_desde_obj)
        except ValueError:
            pass
    
    if fecha_hasta:
        try:
            fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
            equipos_queryset = equipos_queryset.filter(fecha_ingreso__date__lte=fecha_hasta_obj)
        except ValueError:
            pass
    
    # === MÉTRICAS PRINCIPALES ===
    total_equipos = equipos_queryset.count()
    equipos_operativos = equipos_queryset.filter(estado='OPERATIVO').count()
    equipos_mantenimiento = equipos_queryset.filter(estado='MANTENIMIENTO').count()
    equipos_fuera_servicio = equipos_queryset.filter(estado='FUERA_SERVICIO').count()
    
    # Calcular porcentajes
    if total_equipos > 0:
        porcentaje_operativo = round((equipos_operativos / total_equipos) * 100, 1)
        porcentaje_mantenimiento = round((equipos_mantenimiento / total_equipos) * 100, 1)
        porcentaje_fuera_servicio = round((equipos_fuera_servicio / total_equipos) * 100, 1)
    else:
        porcentaje_operativo = porcentaje_mantenimiento = porcentaje_fuera_servicio = 0
    
    # === ANÁLISIS POR SECCIÓN ===
    equipos_por_seccion = equipos_queryset.values('seccion').annotate(
        total=Count('id'),
        operativos=Count(Case(When(estado='OPERATIVO', then=1), output_field=IntegerField())),
        mantenimiento=Count(Case(When(estado='MANTENIMIENTO', then=1), output_field=IntegerField())),
        fuera_servicio=Count(Case(When(estado='FUERA_SERVICIO', then=1), output_field=IntegerField()))
    ).order_by('-total')
    
    # === ANÁLISIS TEMPORAL (últimos 12 meses) ===
    meses_labels = []
    equipos_ingresados_mes = []
    equipos_operativos_mes = []
    equipos_mantenimiento_mes = []
    
    for i in range(12):
        fecha_mes = timezone.now().date().replace(day=1) - timedelta(days=30*i)
        equipos_mes = equipos_queryset.filter(
            fecha_ingreso__year=fecha_mes.year,
            fecha_ingreso__month=fecha_mes.month
        )
        
        meses_labels.insert(0, fecha_mes.strftime('%b %Y'))
        equipos_ingresados_mes.insert(0, equipos_mes.count())
        equipos_operativos_mes.insert(0, equipos_mes.filter(estado='OPERATIVO').count())
        equipos_mantenimiento_mes.insert(0, equipos_mes.filter(estado='MANTENIMIENTO').count())
    
    # === EQUIPOS CON FICHAS TÉCNICAS ===
    equipos_con_ficha = equipos_queryset.filter(ficha_tecnica_completa=True).count()
    equipos_sin_ficha = total_equipos - equipos_con_ficha
    porcentaje_fichas_completas = round((equipos_con_ficha / total_equipos) * 100, 1) if total_equipos > 0 else 0
    
    # === ANÁLISIS DE CRITICIDAD ===
    try:
        planes_mantenimiento = PlanMantenimiento.objects.filter(equipo__in=equipos_queryset)
        equipos_criticos = planes_mantenimiento.filter(prioridad__in=['alta', 'critica']).count()
        equipos_no_criticos = planes_mantenimiento.filter(prioridad__in=['baja', 'media']).count()
    except:
        equipos_criticos = 0
        equipos_no_criticos = 0
    
    # === ALERTAS Y RECOMENDACIONES ===
    alertas = []
    
    # Alerta por equipos fuera de servicio
    if equipos_fuera_servicio > 0:
        alertas.append({
            'tipo': 'danger',
            'titulo': 'Equipos Fuera de Servicio',
            'mensaje': f'{equipos_fuera_servicio} equipos están fuera de servicio y requieren atención inmediata.',
            'accion': 'Revisar estado de equipos'
        })
    
    # Alerta por equipos en mantenimiento
    if equipos_mantenimiento > 5:
        alertas.append({
            'tipo': 'warning',
            'titulo': 'Alto Número de Equipos en Mantenimiento',
            'mensaje': f'{equipos_mantenimiento} equipos están en mantenimiento. Evaluar capacidad de taller.',
            'accion': 'Optimizar programación de mantenimiento'
        })
    
    # Alerta por fichas técnicas incompletas
    if porcentaje_fichas_completas < 70:
        alertas.append({
            'tipo': 'info',
            'titulo': 'Fichas Técnicas Incompletas',
            'mensaje': f'Solo el {porcentaje_fichas_completas}% de equipos tienen fichas técnicas completas.',
            'accion': 'Completar información técnica'
        })
    
    # === OBTENER DATOS PARA FILTROS ===
    secciones_disponibles = Equipo.SECCION_CHOICES
    estados_disponibles = Equipo.ESTADO_CHOICES
    
    # === ÚLTIMOS REPORTES GENERADOS ===
    try:
        ultimos_reportes = ReporteGenerado.objects.filter(
            usuario=request.user,
            tipo_reporte__startswith='equipos_'
        ).order_by('-fecha_generacion')[:5]
    except:
        ultimos_reportes = []
    
    # === PREPARAR DATOS PARA GRÁFICOS ===
    # Datos para gráfico de dona (estados)
    estados_data = {
        'labels': ['Operativo', 'Mantenimiento', 'Fuera de Servicio'],
        'data': [equipos_operativos, equipos_mantenimiento, equipos_fuera_servicio],
        'colors': ['#10b981', '#f59e0b', '#ef4444']
    }
    
    # Datos para gráfico de barras (secciones)
    secciones_labels = []
    secciones_data = []
    secciones_colors = []
    
    colores_secciones = [
        '#3b82f6', '#10b981', '#f59e0b', '#ef4444', 
        '#8b5cf6', '#06b6d4', '#84cc16', '#f97316'
    ]
    
    for i, seccion in enumerate(equipos_por_seccion):
        secciones_labels.append(seccion['seccion'])
        secciones_data.append(seccion['total'])
        secciones_colors.append(colores_secciones[i % len(colores_secciones)])
    
    # === CONTEXTO PARA EL TEMPLATE ===
    context = {
        # Filtros
        'seccion_filtro': seccion_filtro,
        'estado_filtro': estado_filtro,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'tipo_analisis': tipo_analisis,
        
        # Opciones para filtros
        'secciones_disponibles': secciones_disponibles,
        'estados_disponibles': estados_disponibles,
        
        # Métricas principales
        'total_equipos': total_equipos,
        'equipos_operativos': equipos_operativos,
        'equipos_mantenimiento': equipos_mantenimiento,
        'equipos_fuera_servicio': equipos_fuera_servicio,
        'porcentaje_operativo': porcentaje_operativo,
        'porcentaje_mantenimiento': porcentaje_mantenimiento,
        'porcentaje_fuera_servicio': porcentaje_fuera_servicio,
        
        # Análisis por sección
        'equipos_por_seccion': equipos_por_seccion,
        
        # Fichas técnicas
        'equipos_con_ficha': equipos_con_ficha,
        'equipos_sin_ficha': equipos_sin_ficha,
        'porcentaje_fichas_completas': porcentaje_fichas_completas,
        
        # Criticidad
        'equipos_criticos': equipos_criticos,
        'equipos_no_criticos': equipos_no_criticos,
        
        # Alertas
        'alertas': alertas,
        
        # Datos para gráficos (JSON)
        'datos_graficos': json.dumps({
            'categorias': estados_data,
            'estados': estados_data,
            'años': {
                'labels': meses_labels,
                'data': equipos_ingresados_mes
            },
            'ubicaciones': {
                'labels': secciones_labels,
                'data': secciones_data
            }
        }),
        
        # Reportes recientes
        'ultimos_reportes': ultimos_reportes,
        
        'titulo': 'Reportes de Equipos',
    }
    
    return render(request, 'sistema_interno/reportes_equipos.html', context)

@login_required
def exportar_reporte_equipos_excel(request):
    """Exportar reporte de equipos a Excel"""
    
    # Obtener filtros
    seccion_filtro = request.GET.get('seccion', '')
    estado_filtro = request.GET.get('estado', '')
    
    # Obtener datos
    equipos = Equipo.objects.all()
    
    if seccion_filtro:
        equipos = equipos.filter(seccion=seccion_filtro)
    if estado_filtro:
        equipos = equipos.filter(estado=estado_filtro)
    
    # Crear workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Reporte de Equipos"
    
    # Estilos
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="1e40af", end_color="1e40af", fill_type="solid")
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    center_alignment = Alignment(horizontal='center', vertical='center')
    
    # Título del reporte
    ws.merge_cells('A1:J1')
    ws['A1'] = 'REPORTE DE EQUIPOS'
    ws['A1'].font = Font(bold=True, size=16)
    ws['A1'].alignment = center_alignment
    
    # Información del reporte
    ws['A2'] = f'Fecha de generación: {timezone.now().strftime("%d/%m/%Y %H:%M")}'
    ws['A3'] = f'Total de equipos: {equipos.count()}'
    
    # Encabezados (fila 5)
    headers = [
        'Código', 'Nombre', 'Sección', 'Estado', 'Fabricante',
        'Modelo', 'Año', 'Responsable', 'Ubicación', 'Observaciones'
    ]
    
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=5, column=col)
        cell.value = header
        cell.font = header_font
        cell.fill = header_fill
        cell.border = border
        cell.alignment = center_alignment
    
    # Datos
    for row_num, equipo in enumerate(equipos, 6):
        datos = [
            equipo.codigo_interno,
            equipo.nombre,
            equipo.get_seccion_display(),
            equipo.get_estado_display(),
            equipo.fabricante or 'No especificado',
            equipo.modelo or 'No especificado',
            equipo.año_fabricacion or 'No especificado',
            equipo.responsable or 'No asignado',
            equipo.ubicacion_fisica,
            equipo.observaciones or 'Sin observaciones'
        ]
        
        for col, valor in enumerate(datos, 1):
            cell = ws.cell(row=row_num, column=col)
            cell.value = valor
            cell.border = border
            
            # Colorear según estado
            if equipo.estado == 'FUERA_SERVICIO':
                cell.fill = PatternFill(start_color="fee2e2", end_color="fee2e2", fill_type="solid")
            elif equipo.estado == 'MANTENIMIENTO':
                cell.fill = PatternFill(start_color="fef3c7", end_color="fef3c7", fill_type="solid")
    
    # Ajustar ancho de columnas
    for col in range(1, len(headers) + 1):
        column_letter = get_column_letter(col)
        ws.column_dimensions[column_letter].width = 15
    
    # Crear respuesta HTTP
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="Reporte_Equipos_{timezone.now().strftime("%Y%m%d_%H%M")}.xlsx"'
    
    wb.save(response)
    return response

@login_required
def exportar_reporte_equipos_pdf(request):
    """Exportar reporte completo de equipos a PDF con gráficos y estadísticas"""
    
    # Obtener filtros
    seccion_filtro = request.GET.get('seccion', '')
    estado_filtro = request.GET.get('estado', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    
    # Obtener datos filtrados
    equipos_queryset = Equipo.objects.all()
    
    if seccion_filtro:
        equipos_queryset = equipos_queryset.filter(seccion=seccion_filtro)
    if estado_filtro:
        equipos_queryset = equipos_queryset.filter(estado=estado_filtro)
    if fecha_desde:
        try:
            fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
            equipos_queryset = equipos_queryset.filter(fecha_ingreso__date__gte=fecha_desde_obj)
        except ValueError:
            pass
    if fecha_hasta:
        try:
            fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
            equipos_queryset = equipos_queryset.filter(fecha_ingreso__date__lte=fecha_hasta_obj)
        except ValueError:
            pass
    
    # === CALCULAR ESTADÍSTICAS ===
    total_equipos = equipos_queryset.count()
    equipos_operativos = equipos_queryset.filter(estado='OPERATIVO').count()
    equipos_mantenimiento = equipos_queryset.filter(estado='MANTENIMIENTO').count()
    equipos_fuera_servicio = equipos_queryset.filter(estado='FUERA_SERVICIO').count()
    
    # Calcular porcentajes
    if total_equipos > 0:
        porcentaje_operativo = round((equipos_operativos / total_equipos) * 100, 1)
        porcentaje_mantenimiento = round((equipos_mantenimiento / total_equipos) * 100, 1)
        porcentaje_fuera_servicio = round((equipos_fuera_servicio / total_equipos) * 100, 1)
    else:
        porcentaje_operativo = porcentaje_mantenimiento = porcentaje_fuera_servicio = 0
    
    # === ANÁLISIS POR SECCIÓN ===
    equipos_por_seccion = equipos_queryset.values('seccion').annotate(
        total=Count('id'),
        operativos=Count(Case(When(estado='OPERATIVO', then=1), output_field=IntegerField())),
        mantenimiento=Count(Case(When(estado='MANTENIMIENTO', then=1), output_field=IntegerField())),
        fuera_servicio=Count(Case(When(estado='FUERA_SERVICIO', then=1), output_field=IntegerField()))
    ).order_by('-total')
    
    # === CREAR RESPUESTA PDF ===
    response = HttpResponse(content_type='application/pdf')
    timestamp = timezone.now().strftime("%Y%m%d_%H%M")
    filename = f'Reporte_Equipos_{timestamp}.pdf'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # === CREAR DOCUMENTO PDF ===
    doc = SimpleDocTemplate(response, pagesize=A4, topMargin=50, bottomMargin=50)
    story = []
    
    # === ESTILOS ===
    styles = getSampleStyleSheet()
    
    # Estilo para título principal
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=30,
        alignment=1,  # Centro
        textColor=colors.HexColor('#1e40af'),
        fontName='Helvetica-Bold'
    )
    
    # Estilo para subtítulos
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=20,
        textColor=colors.HexColor('#374151'),
        fontName='Helvetica-Bold'
    )
    
    # Estilo para secciones
    section_style = ParagraphStyle(
        'SectionStyle',
        parent=styles['Heading3'],
        fontSize=12,
        spaceAfter=15,
        spaceBefore=20,
        textColor=colors.HexColor('#1e40af'),
        fontName='Helvetica-Bold'
    )
    
    # === ENCABEZADO DEL REPORTE ===
    story.append(Paragraph("REPORTE COMPLETO DE EQUIPOS", title_style))
    story.append(Paragraph("Sistema de Gestión Industrial - Lab Metal Mecánica UMSA", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # === INFORMACIÓN DEL REPORTE ===
    info_data = [
        ['Fecha de generación:', timezone.now().strftime('%d de %B de %Y - %H:%M hrs')],
        ['Total de equipos analizados:', str(total_equipos)],
        ['Filtros aplicados:', generar_texto_filtros(seccion_filtro, estado_filtro, fecha_desde, fecha_hasta)],
        ['Responsable del reporte:', request.user.get_full_name() or request.user.username],
    ]
    
    info_table = Table(info_data, colWidths=[2.5*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
    ]))
    
    story.append(info_table)
    story.append(Spacer(1, 30))
    
    # === RESUMEN EJECUTIVO ===
    story.append(Paragraph("1. RESUMEN EJECUTIVO", section_style))
    
    resumen_data = [
        ['MÉTRICA', 'CANTIDAD', 'PORCENTAJE'],
        ['Equipos Operativos', str(equipos_operativos), f'{porcentaje_operativo}%'],
        ['Equipos en Mantenimiento', str(equipos_mantenimiento), f'{porcentaje_mantenimiento}%'],
        ['Equipos Fuera de Servicio', str(equipos_fuera_servicio), f'{porcentaje_fuera_servicio}%'],
        ['TOTAL', str(total_equipos), '100%'],
    ]
    
    resumen_table = Table(resumen_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
    resumen_table.setStyle(TableStyle([
        # Encabezado
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        
        # Filas de datos
        ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor('#f9fafb')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        
        # Fila total
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e5e7eb')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        
        # Bordes
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    story.append(resumen_table)
    story.append(Spacer(1, 25))
    
    # === DISTRIBUCIÓN POR SECCIÓN ===
    if equipos_por_seccion:
        story.append(Paragraph("2. DISTRIBUCIÓN POR SECCIÓN", section_style))
        
        secciones_data = [['SECCIÓN', 'TOTAL', 'OPERATIVOS', 'MANTENIMIENTO', 'FUERA SERVICIO']]
        
        for seccion in equipos_por_seccion:
            secciones_data.append([
                seccion['seccion'],
                str(seccion['total']),
                str(seccion['operativos']),
                str(seccion['mantenimiento']),
                str(seccion['fuera_servicio'])
            ])
        
        secciones_table = Table(secciones_data, colWidths=[2*inch, 1*inch, 1*inch, 1*inch, 1.2*inch])
        secciones_table.setStyle(TableStyle([
            # Encabezado
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Filas de datos
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0fdf4')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            
            # Bordes y espaciado
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(secciones_table)
        story.append(Spacer(1, 25))
    
    # === DETALLE DE EQUIPOS (MUESTRA LIMITADA) ===
    story.append(Paragraph("3. DETALLE DE EQUIPOS", section_style))
    story.append(Paragraph(f"Mostrando los primeros 20 equipos de {total_equipos} totales", styles['Normal']))
    story.append(Spacer(1, 10))
    
    equipos_data = [['CÓDIGO', 'NOMBRE', 'SECCIÓN', 'ESTADO', 'RESPONSABLE']]
    
    for equipo in equipos_queryset[:20]:
        equipos_data.append([
            equipo.codigo_interno,
            truncar_texto(equipo.nombre, 35),
            equipo.get_seccion_display(),
            equipo.get_estado_display(),
            truncar_texto(equipo.responsable or 'No asignado', 20)
        ])
    
    equipos_table = Table(equipos_data, colWidths=[1.2*inch, 2.3*inch, 1.3*inch, 1.3*inch, 1.2*inch])
    equipos_table.setStyle(TableStyle([
        # Encabezado
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7c3aed')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        
        # Filas alternadas
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fafafa')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('ALIGN', (2, 1), (3, -1), 'CENTER'),
        
        # Bordes
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
    ]))
    
    story.append(equipos_table)
    story.append(Spacer(1, 30))
    
    # === RECOMENDACIONES ===
    story.append(Paragraph("4. ANÁLISIS Y RECOMENDACIONES", section_style))
    
    recomendaciones = generar_recomendaciones(
        total_equipos, equipos_operativos, equipos_mantenimiento, 
        equipos_fuera_servicio, equipos_por_seccion
    )
    
    for i, recomendacion in enumerate(recomendaciones, 1):
        story.append(Paragraph(f"{i}. {recomendacion}", styles['Normal']))
        story.append(Spacer(1, 8))
    
    # === PIE DE PÁGINA ===
    story.append(Spacer(1, 30))
    story.append(Paragraph("___________________________________________", styles['Normal']))
    story.append(Spacer(1, 10))
    
    footer_data = [
        ['Reporte generado por:', request.user.get_full_name() or request.user.username],
        ['Sistema:', 'Gestión Industrial - Lab Metal Mecánica UMSA'],
        ['Fecha y hora:', timezone.now().strftime('%d/%m/%Y %H:%M:%S')],
    ]
    
    footer_table = Table(footer_data, colWidths=[1.5*inch, 4*inch])
    footer_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#6b7280')),
    ]))
    
    story.append(footer_table)
    
    # === CONSTRUIR PDF ===
    doc.build(story)
    
    # === REGISTRAR REPORTE GENERADO ===
    try:
        ReporteGenerado.objects.create(
            titulo=f'Reporte de Equipos {timestamp}',
            tipo_reporte='equipos_general',
            formato='pdf',
            usuario=request.user,
            parametros_filtros={
                'seccion': seccion_filtro,
                'estado': estado_filtro,
                'fecha_desde': fecha_desde,
                'fecha_hasta': fecha_hasta,
            },
            total_registros=total_equipos,
        )
    except:
        pass  # No fallar si no se puede registrar
    
    return response

@login_required
def api_equipos_chart_data(request):
    """API para obtener datos de gráficos de equipos"""
    
    tipo_chart = request.GET.get('tipo', 'estados')
    
    if tipo_chart == 'estados':
        # Datos de estados
        data = {
            'operativo': Equipo.objects.filter(estado='OPERATIVO').count(),
            'mantenimiento': Equipo.objects.filter(estado='MANTENIMIENTO').count(),
            'fuera_servicio': Equipo.objects.filter(estado='FUERA_SERVICIO').count(),
        }
    
    elif tipo_chart == 'secciones':
        # Datos por sección
        secciones = Equipo.objects.values('seccion').annotate(
            total=Count('id')
        ).order_by('-total')
        
        data = {
            'labels': [s['seccion'] for s in secciones],
            'values': [s['total'] for s in secciones]
        }
    
    else:
        data = {'error': 'Tipo de gráfico no válido'}
    
    return JsonResponse(data)


# === FUNCIONES AUXILIARES ===

def generar_texto_filtros(seccion, estado, fecha_desde, fecha_hasta):
    """Genera texto descriptivo de los filtros aplicados"""
    filtros = []
    
    if seccion:
        filtros.append(f"Sección: {seccion}")
    else:
        filtros.append("Sección: Todas")
    
    if estado:
        filtros.append(f"Estado: {estado}")
    else:
        filtros.append("Estado: Todos")
    
    if fecha_desde:
        filtros.append(f"Desde: {fecha_desde}")
    
    if fecha_hasta:
        filtros.append(f"Hasta: {fecha_hasta}")
    
    if not fecha_desde and not fecha_hasta:
        filtros.append("Período: Todo el historial")
    
    return " | ".join(filtros)


def truncar_texto(texto, max_length):
    """Trunca texto para que no exceda el ancho de la tabla"""
    if not texto:
        return ''
    
    if len(texto) <= max_length:
        return texto
    
    return texto[:max_length-3] + '...'


def generar_recomendaciones(total, operativos, mantenimiento, fuera_servicio, por_seccion):
    """Genera recomendaciones basadas en los datos del reporte"""
    recomendaciones = []
    
    if total == 0:
        recomendaciones.append("No se encontraron equipos con los filtros aplicados.")
        return recomendaciones
    
    # Análisis de disponibilidad
    disponibilidad = (operativos / total) * 100 if total > 0 else 0
    
    if disponibilidad >= 85:
        recomendaciones.append(f"Excelente disponibilidad de equipos ({disponibilidad:.1f}%). Mantener el programa actual de mantenimiento.")
    elif disponibilidad >= 70:
        recomendaciones.append(f"Buena disponibilidad de equipos ({disponibilidad:.1f}%). Revisar equipos en mantenimiento para optimizar tiempos.")
    else:
        recomendaciones.append(f"Disponibilidad por debajo del estándar ({disponibilidad:.1f}%). Revisar urgentemente la estrategia de mantenimiento.")
    
    # Análisis de equipos fuera de servicio
    if fuera_servicio > 0:
        porcentaje_fs = (fuera_servicio / total) * 100
        if porcentaje_fs > 15:
            recomendaciones.append(f"Alto porcentaje de equipos fuera de servicio ({porcentaje_fs:.1f}%). Priorizar reparaciones o reemplazos.")
        else:
            recomendaciones.append(f"Atender {fuera_servicio} equipo(s) fuera de servicio para mejorar la disponibilidad.")
    
    # Análisis de mantenimiento
    if mantenimiento > 0:
        porcentaje_mant = (mantenimiento / total) * 100
        if porcentaje_mant > 25:
            recomendaciones.append("Alto porcentaje de equipos en mantenimiento. Evaluar la eficiencia del taller y considerar mantenimiento predictivo.")
        elif porcentaje_mant < 5:
            recomendaciones.append("Muy pocos equipos en mantenimiento. Verificar que se esté cumpliendo el programa de mantenimiento preventivo.")
    
    # Análisis por sección
    if por_seccion:
        seccion_critica = max(por_seccion, key=lambda x: x['fuera_servicio'] + x['mantenimiento'])
        if seccion_critica['fuera_servicio'] + seccion_critica['mantenimiento'] > seccion_critica['operativos']:
            recomendaciones.append(f"La sección {seccion_critica['seccion']} requiere atención prioritaria debido a baja disponibilidad.")
    
    # Recomendación general
    recomendaciones.append("Implementar sistema de monitoreo continuo y mantener actualizado el inventario de repuestos críticos.")
    
    return recomendaciones