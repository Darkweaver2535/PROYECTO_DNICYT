from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Sum, Avg, F
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import date, timedelta
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from django.contrib.auth.models import User  # <-- AGREGAR ESTA LÍNEA
from .models import Repuesto, CategoriaRepuesto, Proveedor, MovimientoStock
from .forms import RepuestoForm
from apps.equipos.models import Equipo
from django.views.decorators.cache import cache_page

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

@login_required
def stock_critico_view(request):
    """Vista para análisis de stock crítico - repuestos con niveles bajos de inventario"""
    
    # Obtener filtros
    categoria_filtro = request.GET.get('categoria', '')
    criticidad_filtro = request.GET.get('criticidad', '')
    estado_filtro = request.GET.get('estado', '')
    proveedor_filtro = request.GET.get('proveedor', '')
    search = request.GET.get('search', '')
    tipo_alerta = request.GET.get('tipo_alerta', '')
    
    # Query base - todos los repuestos activos
    repuestos = Repuesto.objects.filter(activo=True).select_related(
        'categoria', 'proveedor_principal', 'responsable_tecnico'
    )
    
    # === ANÁLISIS DE STOCK CRÍTICO ===
    # Repuestos con stock por debajo del mínimo
    stock_bajo_minimo = repuestos.filter(
        stock_actual__lt=F('stock_minimo')
    ).exclude(stock_minimo=0)
    
    # Repuestos sin stock (agotados)
    repuestos_agotados = repuestos.filter(stock_actual=0)
    
    # Repuestos cerca del punto de reorden
    cerca_reorden = repuestos.filter(
        stock_actual__lte=F('punto_reorden'),
        stock_actual__gt=0
    ).exclude(punto_reorden=0)
    
    # Repuestos críticos con stock bajo
    criticos_stock_bajo = repuestos.filter(
        Q(es_activo_critico=True) | Q(criticidad='CRITICA'),
        stock_actual__lte=F('stock_minimo')
    )
    
    # Repuestos con alta rotación y stock bajo
    alta_rotacion_bajo = repuestos.filter(
        frecuencia_uso__in=['alta', 'muy_alta', 'diaria'],
        stock_actual__lt=F('stock_minimo') + F('stock_seguridad')
    )
    
    # === APLICAR FILTROS ===
    if search:
        repuestos = repuestos.filter(
            Q(nombre__icontains=search) |
            Q(codigo__icontains=search) |
            Q(descripcion__icontains=search) |
            Q(fabricante__icontains=search) |
            Q(codigo_fabricante__icontains=search)
        )
    
    if categoria_filtro:
        repuestos = repuestos.filter(categoria_id=categoria_filtro)
    
    if criticidad_filtro:
        repuestos = repuestos.filter(criticidad=criticidad_filtro)
    
    if estado_filtro:
        repuestos = repuestos.filter(estado=estado_filtro)
    
    if proveedor_filtro:
        repuestos = repuestos.filter(proveedor_principal_id=proveedor_filtro)
    
    # Filtro por tipo de alerta
    if tipo_alerta == 'agotado':
        repuestos = repuestos_agotados
    elif tipo_alerta == 'bajo_minimo':
        repuestos = stock_bajo_minimo
    elif tipo_alerta == 'cerca_reorden':
        repuestos = cerca_reorden
    elif tipo_alerta == 'criticos':
        repuestos = criticos_stock_bajo
    elif tipo_alerta == 'alta_rotacion':
        repuestos = alta_rotacion_bajo
    
    # Calcular métricas para cada repuesto
    repuestos_con_metricas = []
    for repuesto in repuestos:
        # Calcular nivel de alerta
        nivel_alerta = 'normal'
        tipo_problema = []
        
        if repuesto.stock_actual == 0:
            nivel_alerta = 'critico'
            tipo_problema.append('Sin Stock')
        elif repuesto.stock_minimo > 0 and repuesto.stock_actual < repuesto.stock_minimo:
            nivel_alerta = 'alto' if nivel_alerta != 'critico' else 'critico'
            tipo_problema.append('Bajo Mínimo')
        elif repuesto.punto_reorden > 0 and repuesto.stock_actual <= repuesto.punto_reorden:
            nivel_alerta = 'medio' if nivel_alerta == 'normal' else nivel_alerta
            tipo_problema.append('Cerca Reorden')
        
        # Verificar si es crítico
        if repuesto.es_activo_critico or repuesto.criticidad == 'CRITICA':
            if nivel_alerta in ['alto', 'critico']:
                nivel_alerta = 'critico'
                tipo_problema.append('Activo Crítico')
        
        # Calcular días de stock disponible
        if repuesto.stock_actual > 0 and repuesto.precio_unitario > 0:
            # Estimación básica: 30 días de consumo promedio
            consumo_estimado_mensual = max(repuesto.stock_minimo / 2, 1)
            dias_stock = int((repuesto.stock_actual / consumo_estimado_mensual) * 30)
        else:
            dias_stock = 0
        
        # Calcular costo de desabastecimiento
        costo_potencial = repuesto.precio_unitario * repuesto.stock_minimo if repuesto.precio_unitario else 0
        
        repuesto_dict = {
            'repuesto': repuesto,
            'nivel_alerta': nivel_alerta,
            'tipo_problema': tipo_problema,
            'dias_stock': dias_stock,
            'costo_potencial': costo_potencial,
            'porcentaje_stock': (repuesto.stock_actual / max(repuesto.stock_minimo, 1) * 100) if repuesto.stock_minimo > 0 else 0,
        }
        repuestos_con_metricas.append(repuesto_dict)
    
    # Ordenar por nivel de criticidad
    orden_criticidad = {'critico': 0, 'alto': 1, 'medio': 2, 'normal': 3}
    repuestos_con_metricas.sort(key=lambda x: orden_criticidad.get(x['nivel_alerta'], 4))
    
    # === ESTADÍSTICAS GENERALES ===
    total_repuestos = Repuesto.objects.filter(activo=True).count()
    total_agotados = repuestos_agotados.count()
    total_bajo_minimo = stock_bajo_minimo.count()
    total_cerca_reorden = cerca_reorden.count()
    total_criticos_bajo = criticos_stock_bajo.count()
    
    # Valor total en riesgo
    valor_total_riesgo = sum([
        (r.precio_unitario or 0) * (r.stock_minimo - r.stock_actual) 
        for r in stock_bajo_minimo 
        if r.stock_minimo > r.stock_actual
    ])
    
    # Porcentaje de cumplimiento de stock
    repuestos_con_stock_ok = repuestos.filter(
        stock_actual__gte=F('stock_minimo')
    ).exclude(stock_minimo=0).count()
    
    total_con_minimo = repuestos.exclude(stock_minimo=0).count()
    porcentaje_cumplimiento = (repuestos_con_stock_ok / max(total_con_minimo, 1) * 100)
    
    # === ANÁLISIS POR CATEGORÍA ===
    categorias_criticas = {}
    for categoria in CategoriaRepuesto.objects.filter(activo=True):
        repuestos_cat = repuestos.filter(categoria=categoria)
        if repuestos_cat.exists():
            agotados_cat = repuestos_cat.filter(stock_actual=0).count()
            bajo_minimo_cat = repuestos_cat.filter(
                stock_actual__lt=F('stock_minimo')
            ).exclude(stock_minimo=0).count()
            
            total_cat = repuestos_cat.count()
            porcentaje_problemas = ((agotados_cat + bajo_minimo_cat) / max(total_cat, 1)) * 100
            
            if porcentaje_problemas > 0:
                categorias_criticas[categoria.nombre] = {
                    'total': total_cat,
                    'agotados': agotados_cat,
                    'bajo_minimo': bajo_minimo_cat,
                    'porcentaje_problemas': round(porcentaje_problemas, 1),
                    'codigo': categoria.codigo,
                }
    
    # === RECOMENDACIONES AUTOMÁTICAS ===
    recomendaciones = []
    
    if total_agotados > 0:
        recomendaciones.append({
            'tipo': 'danger',
            'titulo': f'{total_agotados} Repuesto(s) Agotado(s)',
            'descripcion': 'Repuestos sin stock disponible - Requieren compra inmediata',
            'accion': 'Generar órdenes de compra urgentes',
            'prioridad': 'urgente'
        })
    
    if total_criticos_bajo > 0:
        recomendaciones.append({
            'tipo': 'danger',
            'titulo': f'{total_criticos_bajo} Activo(s) Crítico(s) con Stock Bajo',
            'descripcion': 'Repuestos críticos por debajo del nivel mínimo',
            'accion': 'Reabastecer inmediatamente',
            'prioridad': 'critica'
        })
    
    if porcentaje_cumplimiento < 80:
        recomendaciones.append({
            'tipo': 'warning',
            'titulo': f'Cumplimiento de Stock: {porcentaje_cumplimiento:.1f}%',
            'descripcion': 'El nivel general de stock está por debajo del objetivo (80%)',
            'accion': 'Revisar políticas de inventario',
            'prioridad': 'alta'
        })
    
    if valor_total_riesgo > 10000:
        recomendaciones.append({
            'tipo': 'info',
            'titulo': f'Valor en Riesgo: ${valor_total_riesgo:,.2f}',
            'descripcion': 'Alto valor monetario en riesgo por desabastecimiento',
            'accion': 'Evaluar impacto financiero',
            'prioridad': 'media'
        })
    
    # === PROVEEDORES PARA FILTROS ===
    proveedores_disponibles = Proveedor.objects.filter(
        activo=True,
        repuestos_principales__in=repuestos
    ).distinct()
    
    categorias_disponibles = CategoriaRepuesto.objects.filter(
        activo=True,
        repuestos__in=repuestos
    ).distinct()
    
    context = {
        # Datos principales
        'repuestos_criticos': repuestos_con_metricas,
        'recomendaciones': recomendaciones,
        
        # Estadísticas generales
        'total_repuestos': total_repuestos,
        'total_agotados': total_agotados,
        'total_bajo_minimo': total_bajo_minimo,
        'total_cerca_reorden': total_cerca_reorden,
        'total_criticos_bajo': total_criticos_bajo,
        'valor_total_riesgo': valor_total_riesgo,
        'porcentaje_cumplimiento': round(porcentaje_cumplimiento, 1),
        
        # Análisis por categoría
        'categorias_criticas': categorias_criticas,
        
        # Filtros aplicados
        'categoria_filtro': categoria_filtro,
        'criticidad_filtro': criticidad_filtro,
        'estado_filtro': estado_filtro,
        'proveedor_filtro': proveedor_filtro,
        'search': search,
        'tipo_alerta': tipo_alerta,
        
        # Opciones para filtros
        'categorias_disponibles': categorias_disponibles,
        'proveedores_disponibles': proveedores_disponibles,
        'criticidades': Repuesto.CRITICIDAD_CHOICES,
        'estados': Repuesto.ESTADO_CHOICES,
        
        # Metadatos
        'titulo': 'Stock Crítico',
        'fecha_actualizacion': timezone.now(),
    }
    
    return render(request, 'sistema_interno/stock_critico.html', context)

from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from django.db.models import F

@login_required
@cache_page(60)  # Cache por 1 minuto
def alertas_stock_api(request):
    """API endpoint para obtener alertas de stock en tiempo real"""
    
    repuestos_agotados = Repuesto.objects.filter(
        activo=True,
        stock_actual=0
    ).count()
    
    repuestos_criticos_bajo = Repuesto.objects.filter(
        activo=True,
        es_activo_critico=True,
        stock_actual__lte=F('stock_minimo')
    ).count()
    
    # SOLO calcular alertas críticas (no incluir todos los bajo mínimo)
    total_alertas_criticas = repuestos_agotados + repuestos_criticos_bajo
    
    return JsonResponse({
        'success': True,
        'alertas': {
            'repuestos_agotados': repuestos_agotados,
            'repuestos_criticos_bajo': repuestos_criticos_bajo,
            'total_alertas_criticas': total_alertas_criticas,
        }
    })

@login_required
def movimientos_stock_view(request):
    """Vista para gestión de movimientos de stock"""
    
    # Filtros
    repuesto_filtro = request.GET.get('repuesto', '')
    tipo_filtro = request.GET.get('tipo', '')
    motivo_filtro = request.GET.get('motivo', '')
    estado_filtro = request.GET.get('estado', '')
    usuario_filtro = request.GET.get('usuario', '')
    proveedor_filtro = request.GET.get('proveedor', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    search = request.GET.get('search', '')
    
    # Query base
    movimientos = MovimientoStock.objects.select_related(
        'repuesto', 'usuario', 'proveedor', 'aprobado_por'
    ).all().order_by('-fecha_movimiento')
    
    # Aplicar filtros
    if search:
        movimientos = movimientos.filter(
            Q(numero_movimiento__icontains=search) |
            Q(repuesto__nombre__icontains=search) |
            Q(repuesto__codigo__icontains=search) |
            Q(motivo_detalle__icontains=search) |
            Q(documento_referencia__icontains=search)
        )
    
    if repuesto_filtro:
        movimientos = movimientos.filter(repuesto_id=repuesto_filtro)
    
    if tipo_filtro:
        movimientos = movimientos.filter(tipo_movimiento=tipo_filtro)
    
    if motivo_filtro:
        movimientos = movimientos.filter(motivo=motivo_filtro)
    
    if estado_filtro:
        movimientos = movimientos.filter(estado=estado_filtro)
    
    if usuario_filtro:
        movimientos = movimientos.filter(usuario_id=usuario_filtro)
    
    if proveedor_filtro:
        movimientos = movimientos.filter(proveedor_id=proveedor_filtro)
    
    # Filtros de fecha
    if fecha_desde:
        try:
            fecha_desde_dt = timezone.datetime.strptime(fecha_desde, '%Y-%m-%d').date()
            movimientos = movimientos.filter(fecha_movimiento__date__gte=fecha_desde_dt)
        except ValueError:
            pass
    
    if fecha_hasta:
        try:
            fecha_hasta_dt = timezone.datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
            movimientos = movimientos.filter(fecha_movimiento__date__lte=fecha_hasta_dt)
        except ValueError:
            pass
    
    # Estadísticas generales
    total_movimientos = movimientos.count()
    
    # Movimientos por tipo en el período filtrado
    entradas = movimientos.filter(
        tipo_movimiento__in=['entrada', 'ajuste_positivo', 'transferencia_entrada', 'devolucion']
    ).count()
    
    salidas = movimientos.filter(
        tipo_movimiento__in=['salida', 'ajuste_negativo', 'transferencia_salida', 'merma']
    ).count()
    
    ajustes = movimientos.filter(
        tipo_movimiento__in=['ajuste_positivo', 'ajuste_negativo']
    ).count()
    
    transferencias = movimientos.filter(
        tipo_movimiento__in=['transferencia_entrada', 'transferencia_salida']
    ).count()
    
    # Movimientos pendientes de aprobación
    pendientes_aprobacion = movimientos.filter(
        requiere_aprobacion=True, 
        estado='pendiente'
    ).count()
    
    # Valor total de movimientos
    valor_total_movimientos = movimientos.aggregate(
        total=Sum('costo_total')
    )['total'] or 0
    
    # Movimientos recientes para alertas
    movimientos_recientes = movimientos[:5]
    
    # Opciones para filtros
    repuestos_disponibles = Repuesto.objects.filter(
        activo=True
    ).distinct().order_by('nombre')
    
    usuarios_disponibles = User.objects.filter(
        is_active=True
    ).distinct().order_by('first_name', 'last_name')
    
    try:
        proveedores_disponibles = Proveedor.objects.filter(
            activo=True
        ).distinct().order_by('nombre')
    except:
        proveedores_disponibles = []
    
    # Paginación
    paginator = Paginator(movimientos, 15)  # 15 movimientos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        # Datos principales
        'movimientos': page_obj,
        'page_obj': page_obj,
        'movimientos_recientes': movimientos_recientes,
        
        # Estadísticas
        'total_movimientos': total_movimientos,
        'entradas': entradas,
        'salidas': salidas,
        'ajustes': ajustes,
        'transferencias': transferencias,
        'pendientes_aprobacion': pendientes_aprobacion,
        'valor_total_movimientos': valor_total_movimientos,
        
        # Filtros aplicados
        'search': search,
        'repuesto_filtro': repuesto_filtro,
        'tipo_filtro': tipo_filtro,
        'motivo_filtro': motivo_filtro,
        'estado_filtro': estado_filtro,
        'usuario_filtro': usuario_filtro,
        'proveedor_filtro': proveedor_filtro,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        
        # Opciones para filtros
        'repuestos_disponibles': repuestos_disponibles,
        'usuarios_disponibles': usuarios_disponibles,
        'proveedores_disponibles': proveedores_disponibles,
        'tipos_movimiento': MovimientoStock.TIPO_MOVIMIENTO_CHOICES,
        'motivos': MovimientoStock.MOTIVO_CHOICES,
        'estados': MovimientoStock.ESTADO_CHOICES,
        
        # Metadatos
        'titulo': 'Movimientos de Stock',
        'fecha_actualizacion': timezone.now(),
    }
    
    return render(request, 'sistema_interno/movimientos.html', context)

@login_required
def crear_movimiento_view(request):
    """Vista para crear nuevo movimiento de stock"""
    
    if request.method == 'POST':
        # Obtener datos del formulario
        repuesto_id = request.POST.get('repuesto')
        tipo_movimiento = request.POST.get('tipo_movimiento')
        motivo = request.POST.get('motivo')
        cantidad = request.POST.get('cantidad')
        costo_unitario = request.POST.get('costo_unitario', 0)
        motivo_detalle = request.POST.get('motivo_detalle', '')
        documento_referencia = request.POST.get('documento_referencia', '')
        ubicacion_destino = request.POST.get('ubicacion_destino', '')
        proveedor_id = request.POST.get('proveedor', '')
        
        try:
            # Validar datos básicos
            if not repuesto_id or not tipo_movimiento or not motivo or not cantidad:
                raise ValueError("Todos los campos obligatorios deben ser completados")
            
            repuesto = get_object_or_404(Repuesto, pk=repuesto_id)
            
            # CONVERTIR CORRECTAMENTE LOS TIPOS DE DATOS
            from decimal import Decimal
            
            cantidad = Decimal(str(cantidad))  # Convertir a Decimal
            costo_unitario = Decimal(str(costo_unitario)) if costo_unitario else Decimal('0')
            
            if cantidad <= 0:
                raise ValueError("La cantidad debe ser mayor a 0")
            
            # Calcular nuevo stock según el tipo de movimiento
            stock_anterior = repuesto.stock_actual  # Ya es Decimal desde el modelo
            
            # Tipos que incrementan stock
            tipos_entrada = ['entrada', 'ajuste_positivo', 'transferencia_entrada', 'devolucion']
            # Tipos que decrementan stock
            tipos_salida = ['salida', 'ajuste_negativo', 'transferencia_salida', 'merma']
            
            if tipo_movimiento in tipos_entrada:
                stock_nuevo = stock_anterior + cantidad  # Decimal + Decimal
                es_entrada = True
            elif tipo_movimiento in tipos_salida:
                stock_nuevo = stock_anterior - cantidad  # Decimal - Decimal
                es_entrada = False
                # Validar stock suficiente para salidas
                if stock_nuevo < 0:
                    raise ValueError(f"Stock insuficiente. Stock actual: {stock_anterior} {repuesto.unidad_medida}")
            else:
                # Para otros tipos, mantener el stock igual
                stock_nuevo = stock_anterior
                es_entrada = None
            
            # Generar número de movimiento único
            from datetime import datetime
            fecha_actual = datetime.now()
            año_actual = fecha_actual.year
            
            # Obtener el último número del año
            ultimo_movimiento = MovimientoStock.objects.filter(
                numero_movimiento__startswith=f'MOV-{año_actual}'
            ).order_by('-numero_movimiento').first()
            
            if ultimo_movimiento:
                try:
                    ultimo_numero = int(ultimo_movimiento.numero_movimiento.split('-')[-1])
                    nuevo_numero = ultimo_numero + 1
                except (ValueError, IndexError):
                    nuevo_numero = 1
            else:
                nuevo_numero = 1
            
            numero_movimiento = f'MOV-{año_actual}-{nuevo_numero:05d}'
            
            # Crear el movimiento
            movimiento = MovimientoStock.objects.create(
                numero_movimiento=numero_movimiento,
                repuesto=repuesto,
                tipo_movimiento=tipo_movimiento,
                motivo=motivo,
                motivo_detalle=motivo_detalle,
                cantidad=cantidad,
                stock_anterior=stock_anterior,
                stock_nuevo=stock_nuevo,
                costo_unitario=costo_unitario,
                costo_total=cantidad * costo_unitario,  # Decimal * Decimal
                usuario=request.user,
                documento_referencia=documento_referencia,
                ubicacion_destino=ubicacion_destino,
                estado='procesado',
                fecha_procesamiento=timezone.now()
            )
            
            # Agregar proveedor si es entrada y se especificó
            if proveedor_id and tipo_movimiento in tipos_entrada:
                try:
                    proveedor = Proveedor.objects.get(pk=proveedor_id)
                    movimiento.proveedor = proveedor
                    movimiento.save()
                except Proveedor.DoesNotExist:
                    pass
            
            # Actualizar stock del repuesto
            repuesto.stock_actual = stock_nuevo
            repuesto.save()
            
            # Determinar el ícono y color del mensaje según el tipo
            if tipo_movimiento in tipos_entrada:
                icono = "⬇️"
                tipo_texto = "entrada"
            elif tipo_movimiento in tipos_salida:
                icono = "⬆️"
                tipo_texto = "salida"
            else:
                icono = "🔄"
                tipo_texto = "ajuste"
            
            # Mensaje de éxito personalizado
            messages.success(
                request,
                f'{icono} Movimiento {movimiento.numero_movimiento} registrado exitosamente.\n'
                f'📦 {repuesto.codigo} - {repuesto.nombre}\n'
                f'📊 Stock: {stock_anterior} → {stock_nuevo} {repuesto.unidad_medida}\n'
                f'💰 Costo total: ${movimiento.costo_total:.2f}'
            )
            
            # Verificar y agregar alertas de stock
            if stock_nuevo <= repuesto.punto_reorden:
                if stock_nuevo <= repuesto.stock_minimo:
                    messages.warning(
                        request,
                        f'⚠️ ALERTA: El stock de {repuesto.nombre} está por debajo del mínimo '
                        f'({repuesto.stock_minimo} {repuesto.unidad_medida}). '
                        f'Stock actual: {stock_nuevo} {repuesto.unidad_medida}'
                    )
                else:
                    messages.info(
                        request,
                        f'📢 AVISO: El stock de {repuesto.nombre} ha alcanzado el punto de reorden '
                        f'({repuesto.punto_reorden} {repuesto.unidad_medida}). '
                        f'Considere realizar un pedido.'
                    )
            
            return redirect('inventario:movimientos')
            
        except ValueError as e:
            messages.error(request, f'❌ Error en los datos: {str(e)}')
        except Exception as e:
            messages.error(request, f'❌ Error al crear el movimiento: {str(e)}')
            print(f"Error detallado: {e}")  # Para debugging
    
    # Datos para el formulario
    repuestos = Repuesto.objects.filter(activo=True).order_by('nombre')
    
    # Proveedores activos
    try:
        proveedores = Proveedor.objects.filter(activo=True).order_by('nombre')
    except:
        proveedores = []
    
    # Verificar si hay repuestos disponibles
    if not repuestos.exists():
        messages.warning(
            request,
            '⚠️ No hay repuestos disponibles para crear movimientos. '
            'Por favor, agregue repuestos al inventario primero.'
        )
    
    context = {
        'repuestos': repuestos,
        'proveedores': proveedores,
        'tipos_movimiento': MovimientoStock.TIPO_MOVIMIENTO_CHOICES,
        'motivos': MovimientoStock.MOTIVO_CHOICES,
        'titulo': 'Crear Movimiento de Stock',
        
        # Estadísticas para mostrar en el contexto si es necesario
        'total_repuestos': repuestos.count(),
        'total_proveedores': len(proveedores),
    }
    
    return render(request, 'sistema_interno/crear_movimiento.html', context)