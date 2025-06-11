from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Sum, Avg, F
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import date, timedelta
import json
import csv
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from .models import Repuesto, CategoriaRepuesto, Proveedor, MovimientoStock
from .forms import RepuestoForm
from apps.equipos.models import Equipo

@login_required
def repuestos_view(request):
    """Vista principal de inventario de repuestos"""
    
    # Filtros
    search_query = request.GET.get('search', '')
    categoria_filtro = request.GET.get('categoria', '')
    estado_filtro = request.GET.get('estado', '')
    criticidad_filtro = request.GET.get('criticidad', '')
    proveedor_filtro = request.GET.get('proveedor', '')
    stock_filtro = request.GET.get('stock', '')  # bajo, agotado, normal
    
    # Query base
    repuestos = Repuesto.objects.select_related('categoria', 'proveedor_principal').all()
    
    # Aplicar filtros
    if search_query:
        repuestos = repuestos.filter(
            Q(codigo__icontains=search_query) |
            Q(nombre__icontains=search_query) |
            Q(descripcion__icontains=search_query) |
            Q(codigo_fabricante__icontains=search_query) |
            Q(numero_parte__icontains=search_query) |
            Q(fabricante__icontains=search_query)
        )
    
    if categoria_filtro:
        repuestos = repuestos.filter(categoria_id=categoria_filtro)
    
    if estado_filtro:
        repuestos = repuestos.filter(estado=estado_filtro)
    
    if criticidad_filtro:
        repuestos = repuestos.filter(criticidad=criticidad_filtro)
    
    if proveedor_filtro:
        repuestos = repuestos.filter(proveedor_principal_id=proveedor_filtro)
    
    if stock_filtro:
        if stock_filtro == 'agotado':
            repuestos = repuestos.filter(stock_actual=0)
        elif stock_filtro == 'bajo':
            repuestos = repuestos.filter(stock_actual__lte=F('punto_reorden'), stock_actual__gt=0)
        elif stock_filtro == 'normal':
            repuestos = repuestos.filter(stock_actual__gt=F('punto_reorden'))
    
    # Calcular métricas para cada repuesto
    for repuesto in repuestos:
        repuesto.necesita_reorden = repuesto.necesita_reposicion()
        repuesto.dias_vencimiento = repuesto.dias_hasta_vencimiento()
        repuesto.valor_total = repuesto.valor_stock_actual()
    
    # Estadísticas generales
    total_repuestos = repuestos.count()
    repuestos_disponibles = repuestos.filter(estado='disponible').count()
    repuestos_agotados = repuestos.filter(estado='agotado').count()
    repuestos_bajo_stock = repuestos.filter(stock_actual__lte=F('punto_reorden')).count()
    repuestos_criticos = repuestos.filter(criticidad='critica').count()
    
    # Valor total del inventario
    valor_total_inventario = sum(r.valor_total for r in repuestos if r.valor_total)
    
    # Repuestos próximos a vencer (30 días)
    proximos_vencer = repuestos.filter(
        fecha_vencimiento__lte=date.today() + timedelta(days=30),
        fecha_vencimiento__gt=date.today()
    ).count()
    
    # Alertas
    alertas = []
    
    if repuestos_agotados > 0:
        alertas.append({
            'tipo': 'danger',
            'icono': 'bi-exclamation-triangle-fill',
            'titulo': f'{repuestos_agotados} Repuesto(s) Agotado(s)',
            'descripcion': 'Requieren reposición inmediata',
        })
    
    if repuestos_bajo_stock > 0:
        alertas.append({
            'tipo': 'warning',
            'icono': 'bi-exclamation-triangle',
            'titulo': f'{repuestos_bajo_stock} Repuesto(s) Bajo Stock',
            'descripcion': 'Stock por debajo del punto de reorden',
        })
    
    if proximos_vencer > 0:
        alertas.append({
            'tipo': 'info',
            'icono': 'bi-clock',
            'titulo': f'{proximos_vencer} Repuesto(s) Próximos a Vencer',
            'descripcion': 'Vencen en los próximos 30 días',
        })
    
    # Obtener datos para filtros
    categorias = CategoriaRepuesto.objects.filter(activo=True).order_by('nombre')
    proveedores = Proveedor.objects.filter(activo=True).order_by('nombre')
    
    # Paginación
    paginator = Paginator(repuestos, 12)  # 12 repuestos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'repuestos': page_obj,
        'page_obj': page_obj,
        'search_query': search_query,
        'categoria_filtro': categoria_filtro,
        'estado_filtro': estado_filtro,
        'criticidad_filtro': criticidad_filtro,
        'proveedor_filtro': proveedor_filtro,
        'stock_filtro': stock_filtro,
        
        # Opciones para filtros
        'categorias': categorias,
        'proveedores': proveedores,
        'estados': Repuesto.ESTADO_CHOICES,
        'criticidades': Repuesto.CRITICIDAD_CHOICES,
        
        # Estadísticas
        'total_repuestos': total_repuestos,
        'repuestos_disponibles': repuestos_disponibles,
        'repuestos_agotados': repuestos_agotados,
        'repuestos_bajo_stock': repuestos_bajo_stock,
        'repuestos_criticos': repuestos_criticos,
        'proximos_vencer': proximos_vencer,
        'valor_total_inventario': valor_total_inventario,
        'alertas': alertas,
        
        'titulo': 'Inventario de Repuestos',
    }
    
    return render(request, 'sistema_interno/repuestos.html', context)

@login_required
def crear_repuesto_view(request):
    """Vista para crear nuevo repuesto"""
    
    if request.method == 'POST':
        form = RepuestoForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                repuesto = form.save(commit=False)
                repuesto.creado_por = request.user
                repuesto.save()
                
                # Crear movimiento inicial de stock si hay stock inicial
                if repuesto.stock_actual > 0:
                    MovimientoStock.objects.create(
                        repuesto=repuesto,
                        tipo_movimiento='entrada',
                        cantidad=repuesto.stock_actual,
                        stock_anterior=0,
                        stock_nuevo=repuesto.stock_actual,
                        motivo='Stock inicial al crear repuesto',
                        usuario=request.user
                    )
                
                messages.success(
                    request,
                    f'✅ Repuesto "{repuesto.nombre}" creado exitosamente con código {repuesto.codigo}'
                )
                return redirect('inventario:repuestos')
                
            except Exception as e:
                messages.error(
                    request,
                    f'❌ Error al crear el repuesto: {str(e)}'
                )
        else:
            # Crear mensaje de error más específico
            error_fields = []
            for field, errors in form.errors.items():
                field_name = form.fields[field].label or field
                error_fields.append(f"{field_name}: {', '.join(errors)}")
            
            if error_fields:
                messages.error(
                    request,
                    f"❌ Por favor corrija los siguientes errores: {'; '.join(error_fields)}"
                )
            else:
                messages.error(request, "❌ Error en el formulario. Por favor verifique los datos.")
    else:
        form = RepuestoForm()
    
    # Estadísticas para el contexto
    stats = {
        'total_repuestos': Repuesto.objects.count(),
        'total_categorias': CategoriaRepuesto.objects.filter(activo=True).count(),
        'total_proveedores': Proveedor.objects.filter(activo=True).count(),
    }
    
    context = {
        'form': form,
        'accion': 'crear',
        'titulo': 'Crear Nuevo Repuesto',
        'stats': stats,
    }
    
    return render(request, 'sistema_interno/crear_repuesto.html', context)

@login_required
def editar_repuesto_view(request, pk):
    """Vista para editar repuesto existente"""
    
    repuesto = get_object_or_404(Repuesto, pk=pk)
    
    if request.method == 'POST':
        form = RepuestoForm(request.POST, request.FILES, instance=repuesto)
        if form.is_valid():
            try:
                repuesto_actualizado = form.save()
                
                messages.success(
                    request,
                    f'✅ Repuesto "{repuesto_actualizado.nombre}" actualizado exitosamente'
                )
                return redirect('inventario:repuesto-detalle', pk=repuesto_actualizado.pk)
                
            except Exception as e:
                messages.error(
                    request,
                    f'❌ Error al actualizar el repuesto: {str(e)}'
                )
        else:
            # Crear mensaje de error específico
            error_fields = []
            for field, errors in form.errors.items():
                field_name = form.fields[field].label or field
                error_fields.append(f"{field_name}: {', '.join(errors)}")
            
            if error_fields:
                messages.error(
                    request,
                    f"❌ Por favor corrija los siguientes errores: {'; '.join(error_fields)}"
                )
            else:
                messages.error(request, "❌ Error en el formulario. Por favor verifique los datos.")
    else:
        form = RepuestoForm(instance=repuesto)
    
    context = {
        'form': form,
        'repuesto': repuesto,
        'accion': 'editar',
        'titulo': f'Editar Repuesto - {repuesto.codigo}',
    }
    
    return render(request, 'sistema_interno/crear_repuesto.html', context)

@login_required
def exportar_repuestos_view(request):
    """Vista para exportar repuestos a Excel"""
    
    # Obtener los mismos filtros que la vista principal
    search_query = request.GET.get('search', '')
    categoria_filtro = request.GET.get('categoria', '')
    estado_filtro = request.GET.get('estado', '')
    criticidad_filtro = request.GET.get('criticidad', '')
    proveedor_filtro = request.GET.get('proveedor', '')
    stock_filtro = request.GET.get('stock', '')
    formato = request.GET.get('formato', 'excel')  # excel o csv
    
    # Query base con los mismos filtros
    repuestos = Repuesto.objects.select_related('categoria', 'proveedor_principal').all()
    
    # Aplicar los mismos filtros
    if search_query:
        repuestos = repuestos.filter(
            Q(codigo__icontains=search_query) |
            Q(nombre__icontains=search_query) |
            Q(descripcion__icontains=search_query) |
            Q(codigo_fabricante__icontains=search_query) |
            Q(numero_parte__icontains=search_query) |
            Q(fabricante__icontains=search_query)
        )
    
    if categoria_filtro:
        repuestos = repuestos.filter(categoria_id=categoria_filtro)
    
    if estado_filtro:
        repuestos = repuestos.filter(estado=estado_filtro)
    
    if criticidad_filtro:
        repuestos = repuestos.filter(criticidad=criticidad_filtro)
    
    if proveedor_filtro:
        repuestos = repuestos.filter(proveedor_principal_id=proveedor_filtro)
    
    if stock_filtro:
        if stock_filtro == 'agotado':
            repuestos = repuestos.filter(stock_actual=0)
        elif stock_filtro == 'bajo':
            repuestos = repuestos.filter(stock_actual__lte=F('punto_reorden'), stock_actual__gt=0)
        elif stock_filtro == 'normal':
            repuestos = repuestos.filter(stock_actual__gt=F('punto_reorden'))
    
    if formato == 'csv':
        return exportar_csv(repuestos)
    else:
        return exportar_excel(repuestos)

def exportar_csv(repuestos):
    """Exportar repuestos a CSV"""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="inventario_repuestos_{date.today().strftime("%Y%m%d")}.csv"'
    
    # Agregar BOM para UTF-8
    response.write('\ufeff')
    
    writer = csv.writer(response)
    
    # Escribir encabezados
    headers = [
        'Código', 'Nombre', 'Descripción', 'Categoría', 'Fabricante',
        'Código Fabricante', 'Número de Parte', 'Stock Actual', 'Stock Mínimo',
        'Stock Máximo', 'Punto Reorden', 'Unidad Medida', 'Precio Unitario',
        'Estado', 'Criticidad', 'Proveedor Principal', 'Ubicación Almacén',
        'Fecha Vencimiento', 'Fecha Última Compra', 'Es Consumible',
        'Requiere Refrigeración', 'Observaciones'
    ]
    writer.writerow(headers)
    
    # Escribir datos
    for repuesto in repuestos:
        row = [
            repuesto.codigo,
            repuesto.nombre,
            repuesto.descripcion,
            repuesto.categoria.nombre if repuesto.categoria else '',
            repuesto.fabricante or '',
            repuesto.codigo_fabricante or '',
            repuesto.numero_parte or '',
            float(repuesto.stock_actual),
            float(repuesto.stock_minimo),
            float(repuesto.stock_maximo),
            float(repuesto.punto_reorden),
            repuesto.get_unidad_medida_display(),
            float(repuesto.precio_unitario),
            repuesto.get_estado_display(),
            repuesto.get_criticidad_display(),
            repuesto.proveedor_principal.nombre if repuesto.proveedor_principal else '',
            repuesto.ubicacion_almacen or '',
            repuesto.fecha_vencimiento.strftime('%Y-%m-%d') if repuesto.fecha_vencimiento else '',
            repuesto.fecha_ultima_compra.strftime('%Y-%m-%d') if repuesto.fecha_ultima_compra else '',
            'Sí' if repuesto.es_consumible else 'No',
            'Sí' if repuesto.requiere_refrigeracion else 'No',
            repuesto.observaciones or ''
        ]
        writer.writerow(row)
    
    return response

def exportar_excel(repuestos):
    """Exportar repuestos a Excel con formato"""
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Inventario de Repuestos"
    
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
    
    # Encabezados
    headers = [
        'Código', 'Nombre', 'Descripción', 'Categoría', 'Fabricante',
        'Código Fabricante', 'Número de Parte', 'Stock Actual', 'Stock Mínimo',
        'Stock Máximo', 'Punto Reorden', 'Unidad', 'Precio Unitario',
        'Valor Total', 'Estado', 'Criticidad', 'Proveedor', 'Ubicación',
        'Fecha Vencimiento', 'Días Vencimiento', 'Necesita Reposición'
    ]
    
    # Escribir encabezados con estilo
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center_alignment
        cell.border = border
    
    # Escribir datos
    for row_num, repuesto in enumerate(repuestos, 2):
        # Calcular métricas
        valor_total = repuesto.valor_stock_actual()
        dias_vencimiento = repuesto.dias_hasta_vencimiento()
        necesita_reposicion = repuesto.necesita_reposicion()
        
        data = [
            repuesto.codigo,
            repuesto.nombre,
            repuesto.descripcion,
            repuesto.categoria.nombre if repuesto.categoria else '',
            repuesto.fabricante or '',
            repuesto.codigo_fabricante or '',
            repuesto.numero_parte or '',
            float(repuesto.stock_actual),
            float(repuesto.stock_minimo),
            float(repuesto.stock_maximo),
            float(repuesto.punto_reorden),
            repuesto.get_unidad_medida_display(),
            float(repuesto.precio_unitario),
            float(valor_total),
            repuesto.get_estado_display(),
            repuesto.get_criticidad_display(),
            repuesto.proveedor_principal.nombre if repuesto.proveedor_principal else '',
            repuesto.ubicacion_almacen or '',
            repuesto.fecha_vencimiento if repuesto.fecha_vencimiento else '',
            dias_vencimiento if dias_vencimiento is not None else '',
            'Sí' if necesita_reposicion else 'No'
        ]
        
        for col, value in enumerate(data, 1):
            cell = ws.cell(row=row_num, column=col, value=value)
            cell.border = border
            
            # Aplicar colores según estado
            if col == 15:  # Columna Estado
                if value == 'Agotado':
                    cell.fill = PatternFill(start_color="ffebee", end_color="ffebee", fill_type="solid")
                elif value == 'Por Vencer':
                    cell.fill = PatternFill(start_color="fff3e0", end_color="fff3e0", fill_type="solid")
                elif value == 'Disponible':
                    cell.fill = PatternFill(start_color="e8f5e8", end_color="e8f5e8", fill_type="solid")
            
            elif col == 16:  # Columna Criticidad
                if value == 'Crítica':
                    cell.fill = PatternFill(start_color="ffebee", end_color="ffebee", fill_type="solid")
                elif value == 'Alta':
                    cell.fill = PatternFill(start_color="fff3e0", end_color="fff3e0", fill_type="solid")
            
            elif col == 21:  # Columna Necesita Reposición
                if value == 'Sí':
                    cell.fill = PatternFill(start_color="fff3e0", end_color="fff3e0", fill_type="solid")
    
    # Ajustar ancho de columnas
    for col in range(1, len(headers) + 1):
        column_letter = get_column_letter(col)
        if col in [3]:  # Descripción
            ws.column_dimensions[column_letter].width = 40
        elif col in [1, 2, 4, 5, 17, 18]:  # Código, Nombre, Categoría, Fabricante, Proveedor, Ubicación
            ws.column_dimensions[column_letter].width = 20
        elif col in [6, 7]:  # Códigos
            ws.column_dimensions[column_letter].width = 15
        else:
            ws.column_dimensions[column_letter].width = 12
    
    # Crear respuesta HTTP
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="inventario_repuestos_{date.today().strftime("%Y%m%d")}.xlsx"'
    
    wb.save(response)
    return response

@login_required
def repuesto_detalle_view(request, pk):
    """Vista detallada de un repuesto"""
    repuesto = get_object_or_404(Repuesto, pk=pk)
    
    # Obtener movimientos recientes
    movimientos_recientes = repuesto.movimientos.order_by('-fecha_movimiento')[:10]
    
    # Calcular métricas
    repuesto.necesita_reorden = repuesto.necesita_reposicion()
    repuesto.dias_vencimiento = repuesto.dias_hasta_vencimiento()
    repuesto.valor_total = repuesto.valor_stock_actual()
    
    context = {
        'repuesto': repuesto,
        'movimientos_recientes': movimientos_recientes,
    }
    
    return render(request, 'sistema_interno/repuesto_detalle.html', context)

@login_required
def dashboard_inventario_view(request):
    """Dashboard principal del inventario"""
    
    # Métricas generales
    total_repuestos = Repuesto.objects.filter(activo=True).count()
    repuestos_criticos = Repuesto.objects.filter(criticidad='critica', activo=True).count()
    repuestos_agotados = Repuesto.objects.filter(estado='agotado', activo=True).count()
    
    # Valor total del inventario
    repuestos_con_valor = Repuesto.objects.filter(activo=True, precio_unitario__gt=0)
    valor_total = sum(r.stock_actual * r.precio_unitario for r in repuestos_con_valor)
    
    # Repuestos que necesitan reposición
    necesitan_reposicion = Repuesto.objects.filter(
        stock_actual__lte=F('punto_reorden'), 
        activo=True
    ).count()
    
    # Movimientos recientes
    movimientos_recientes = MovimientoStock.objects.select_related(
        'repuesto', 'usuario'
    ).order_by('-fecha_movimiento')[:5]
    
    # Top 5 repuestos más utilizados (por movimientos de salida)
    repuestos_mas_utilizados = Repuesto.objects.filter(
        movimientos__tipo_movimiento='salida',
        activo=True
    ).annotate(
        total_salidas=Sum('movimientos__cantidad')
    ).order_by('-total_salidas')[:5]
    
    context = {
        'total_repuestos': total_repuestos,
        'repuestos_criticos': repuestos_criticos,
        'repuestos_agotados': repuestos_agotados,
        'valor_total': valor_total,
        'necesitan_reposicion': necesitan_reposicion,
        'movimientos_recientes': movimientos_recientes,
        'repuestos_mas_utilizados': repuestos_mas_utilizados,
        'titulo': 'Dashboard Inventario',
    }
    
    return render(request, 'sistema_interno/dashboard_inventario.html', context)