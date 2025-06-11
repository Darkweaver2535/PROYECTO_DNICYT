from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Sum, Avg, F
from django.db.models.functions import TruncMonth, TruncWeek, TruncDate
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal

# CORREGIR ESTAS IMPORTACIONES:
from .models import Material, CategoriaMaterial, MovimientoMaterial
from apps.inventario.models import Proveedor  # <- IMPORTAR DESDE INVENTARIO
from .forms import MaterialForm, MovimientoMaterialForm

@login_required
def materiales_view(request):
    """Vista principal de materiales"""
    
    # Filtros
    search_query = request.GET.get('search', '')
    categoria_filtro = request.GET.get('categoria', '')
    estado_filtro = request.GET.get('estado', '')
    criticidad_filtro = request.GET.get('criticidad', '')
    proveedor_filtro = request.GET.get('proveedor', '')
    tipo_filtro = request.GET.get('tipo', '')
    
    # Query base
    materiales = Material.objects.select_related('categoria', 'proveedor_principal').all()
    
    # Aplicar filtros
    if search_query:
        materiales = materiales.filter(
            Q(codigo__icontains=search_query) |
            Q(nombre__icontains=search_query) |
            Q(descripcion__icontains=search_query) |
            Q(marca__icontains=search_query) |
            Q(modelo__icontains=search_query)
        )
    
    if categoria_filtro:
        materiales = materiales.filter(categoria_id=categoria_filtro)
    
    if estado_filtro:
        materiales = materiales.filter(estado=estado_filtro)
    
    if criticidad_filtro:
        materiales = materiales.filter(criticidad=criticidad_filtro)
    
    if proveedor_filtro:
        materiales = materiales.filter(proveedor_principal_id=proveedor_filtro)
    
    if tipo_filtro:
        materiales = materiales.filter(tipo=tipo_filtro)
    
    # Calcular métricas para cada material
    for material in materiales:
        material.valor_total = material.valor_stock_actual()
        material.necesita_reorden = material.necesita_reposicion()
        material.dias_vencimiento = material.dias_hasta_vencimiento()
    
    # Estadísticas
    total_materiales = materiales.count()
    materiales_disponibles = materiales.filter(estado='disponible').count()
    materiales_agotados = materiales.filter(estado='agotado').count()
    materiales_bajo_stock = materiales.filter(stock_actual__lte=F('stock_minimo')).count()
    materiales_criticos = materiales.filter(criticidad='critica').count()
    
    # Valor total del inventario
    valor_total_inventario = sum(m.valor_total for m in materiales if m.valor_total)
    
    # Materiales próximos a vencer (30 días)
    proximos_vencer = materiales.filter(
        fecha_vencimiento__lte=date.today() + timedelta(days=30),
        fecha_vencimiento__gt=date.today()
    ).count()
    
    # Alertas
    alertas = []
    
    if materiales_agotados > 0:
        alertas.append({
            'tipo': 'danger',
            'icono': 'bi-exclamation-triangle-fill',
            'titulo': f'{materiales_agotados} Material(es) Agotado(s)',
            'descripcion': 'Materiales sin stock que requieren reposición inmediata.'
        })
    
    if materiales_bajo_stock > 0:
        alertas.append({
            'tipo': 'warning',
            'icono': 'bi-arrow-down-circle',
            'titulo': f'{materiales_bajo_stock} Material(es) con Stock Bajo',
            'descripcion': 'Materiales por debajo del nivel mínimo de stock.'
        })
    
    if proximos_vencer > 0:
        alertas.append({
            'tipo': 'info',
            'icono': 'bi-calendar-event',
            'titulo': f'{proximos_vencer} Material(es) Próximo(s) a Vencer',
            'descripcion': 'Materiales que vencen en los próximos 30 días.'
        })
    
    # Obtener datos para filtros
    categorias = CategoriaMaterial.objects.filter(activo=True).order_by('nombre')
    proveedores = Proveedor.objects.filter(activo=True).order_by('nombre')
    
    # Paginación
    paginator = Paginator(materiales, 12)  # 12 materiales por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'materiales': page_obj,
        'page_obj': page_obj,
        'search_query': search_query,
        'categoria_filtro': categoria_filtro,
        'estado_filtro': estado_filtro,
        'criticidad_filtro': criticidad_filtro,
        'proveedor_filtro': proveedor_filtro,
        'tipo_filtro': tipo_filtro,
        'categorias': categorias,
        'proveedores': proveedores,
        'estados': Material.ESTADO_CHOICES,
        'criticidades': Material.CRITICIDAD_CHOICES,
        'tipos': Material.TIPO_CHOICES,
        'total_materiales': total_materiales,
        'materiales_disponibles': materiales_disponibles,
        'materiales_agotados': materiales_agotados,
        'materiales_bajo_stock': materiales_bajo_stock,
        'materiales_criticos': materiales_criticos,
        'proximos_vencer': proximos_vencer,
        'valor_total_inventario': valor_total_inventario,
        'alertas': alertas,
        'titulo': 'Materiales',
    }
    
    return render(request, 'sistema_interno/materiales.html', context)

@login_required
def crear_material_view(request):
    """Vista para crear nuevo material"""
    
    if request.method == 'POST':
        print(f"DEBUG CREAR: POST recibido - datos: {request.POST}")  # Debug
        form = MaterialForm(request.POST, request.FILES)
        
        print(f"DEBUG CREAR: Form errors: {form.errors}")  # Debug
        print(f"DEBUG CREAR: Form is valid: {form.is_valid()}")  # Debug
        
        if form.is_valid():
            print("DEBUG CREAR: Formulario válido, guardando...")  # Debug
            try:
                material = form.save()
                print(f"DEBUG CREAR: Material guardado: {material.codigo}")  # Debug
                messages.success(
                    request, 
                    f'✅ Material "{material.codigo} - {material.nombre}" creado exitosamente.'
                )
                return redirect('materiales:material-detalle', pk=material.pk)
            except Exception as e:
                print(f"DEBUG CREAR: Error al guardar: {e}")  # Debug
                messages.error(
                    request, 
                    f'Error al guardar el material: {str(e)}'
                )
        else:
            print(f"DEBUG CREAR: Errores del formulario: {form.errors}")  # Debug
            # Mostrar errores específicos
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
            
            messages.error(
                request, 
                'Error al crear el material. Por favor revise los campos marcados.'
            )
    else:
        form = MaterialForm()
    
    # Estadísticas para el contexto
    stats = {
        'total_materiales': Material.objects.count(),
        'total_categorias': CategoriaMaterial.objects.filter(activo=True).count(),
        'total_proveedores': Proveedor.objects.filter(activo=True).count(),
    }
    
    context = {
        'form': form,
        'accion': 'crear',
        'titulo': 'Crear Nuevo Material',
        'stats': stats,
    }
    
    return render(request, 'sistema_interno/crear_material.html', context)

@login_required
def material_detalle_view(request, pk):
    """Vista detallada de un material"""
    
    material = get_object_or_404(Material, pk=pk)
    
    # Obtener movimientos recientes
    movimientos_recientes = material.movimientos.order_by('-fecha_movimiento')[:5]
    
    # Calcular métricas adicionales
    material.valor_stock = material.valor_stock_actual()
    material.dias_hasta_vencimiento = material.dias_hasta_vencimiento()
    
    # Generar alertas
    alertas = []
    
    # Alertas de stock
    if material.stock_actual <= 0:
        alertas.append({
            'tipo': 'danger',
            'icono': 'bi-exclamation-triangle-fill',
            'titulo': 'Material Agotado',
            'descripcion': 'El stock actual es 0. Se requiere reposición inmediata.'
        })
    elif material.stock_actual <= material.stock_minimo:
        alertas.append({
            'tipo': 'warning',
            'icono': 'bi-exclamation-triangle',
            'titulo': 'Stock Bajo',
            'descripcion': f'El stock actual ({material.stock_actual}) está por debajo del mínimo ({material.stock_minimo}).'
        })
    
    # Alertas de vencimiento
    if material.dias_hasta_vencimiento is not None:
        if material.dias_hasta_vencimiento < 0:
            alertas.append({
                'tipo': 'danger',
                'icono': 'bi-calendar-x',
                'titulo': 'Material Vencido',
                'descripcion': f'Este material venció hace {abs(material.dias_hasta_vencimiento)} días.'
            })
        elif material.dias_hasta_vencimiento <= 30:
            alertas.append({
                'tipo': 'warning',
                'icono': 'bi-calendar-event',
                'titulo': 'Próximo a Vencer',
                'descripcion': f'Este material vence en {material.dias_hasta_vencimiento} días.'
            })
    
    # Alertas de calibración (para herramientas)
    if material.tipo == 'herramienta' and material.necesita_calibracion():
        alertas.append({
            'tipo': 'info',
            'icono': 'bi-tools',
            'titulo': 'Calibración Requerida',
            'descripcion': 'Esta herramienta requiere calibración.'
        })
    
    context = {
        'material': material,
        'movimientos_recientes': movimientos_recientes,
        'alertas': alertas,
    }
    
    return render(request, 'sistema_interno/material_detalle.html', context)

@login_required
def editar_material_view(request, pk):
    """Vista para editar material existente"""
    
    material = get_object_or_404(Material, pk=pk)
    
    if request.method == 'POST':
        form = MaterialForm(request.POST, request.FILES, instance=material)
        if form.is_valid():
            material_actualizado = form.save()
            messages.success(
                request, 
                f'✅ Material "{material_actualizado.codigo}" actualizado exitosamente.'
            )
            return redirect('materiales:material-detalle', pk=material_actualizado.pk)
        else:
            messages.error(
                request, 
                'Error al actualizar el material. Por favor revise los campos marcados.'
            )
    else:
        form = MaterialForm(instance=material)
    
    context = {
        'form': form,
        'material': material,
        'accion': 'editar',
        'titulo': f'Editar Material - {material.codigo}',
    }
    
    return render(request, 'sistema_interno/crear_material.html', context)

@login_required
def crear_movimiento_view(request, material_pk=None):
    """Vista para crear movimiento de material"""
    
    material = None
    if material_pk:
        material = get_object_or_404(Material, pk=material_pk)
    
    if request.method == 'POST':
        form = MovimientoMaterialForm(request.POST)
        if form.is_valid():
            movimiento = form.save(commit=False)
            movimiento.usuario = request.user
            movimiento.stock_anterior = movimiento.material.stock_actual
            
            # Calcular nuevo stock según el tipo de movimiento
            if movimiento.tipo_movimiento in ['entrada', 'ajuste_positivo', 'devolucion']:
                nuevo_stock = movimiento.stock_anterior + movimiento.cantidad
            else:  # salida, ajuste_negativo, merma, transferencia
                nuevo_stock = movimiento.stock_anterior - movimiento.cantidad
            
            movimiento.stock_nuevo = max(nuevo_stock, 0)  # No permitir stock negativo
            movimiento.costo_total = movimiento.cantidad * movimiento.costo_unitario
            
            # Guardar movimiento
            movimiento.save()
            
            # Actualizar stock del material
            movimiento.material.stock_actual = movimiento.stock_nuevo
            movimiento.material.save()
            
            messages.success(
                request,
                f'✅ Movimiento registrado exitosamente. Stock actualizado: {movimiento.stock_nuevo}'
            )
            return redirect('materiales:material-detalle', pk=movimiento.material.pk)
        else:
            messages.error(
                request,
                'Error al registrar el movimiento. Por favor revise los campos.'
            )
    else:
        form = MovimientoMaterialForm()
        if material:
            form.fields['material'].initial = material
    
    context = {
        'form': form,
        'material': material,
        'titulo': 'Registrar Movimiento de Material',
    }
    
    return render(request, 'sistema_interno/crear_movimiento.html', context)

@login_required
def movimientos_view(request):
    """Vista para listar movimientos de materiales"""
    
    # Filtros
    material_filtro = request.GET.get('material', '')
    tipo_filtro = request.GET.get('tipo', '')
    motivo_filtro = request.GET.get('motivo', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    
    # Query base
    movimientos = MovimientoMaterial.objects.select_related('material', 'usuario').all()
    
    # Aplicar filtros
    if material_filtro:
        movimientos = movimientos.filter(material_id=material_filtro)
    
    if tipo_filtro:
        movimientos = movimientos.filter(tipo_movimiento=tipo_filtro)
    
    if motivo_filtro:
        movimientos = movimientos.filter(motivo=motivo_filtro)
    
    if fecha_desde:
        movimientos = movimientos.filter(fecha_movimiento__date__gte=fecha_desde)
    
    if fecha_hasta:
        movimientos = movimientos.filter(fecha_movimiento__date__lte=fecha_hasta)
    
    # Ordenar por fecha descendente
    movimientos = movimientos.order_by('-fecha_movimiento')
    
    # Paginación
    paginator = Paginator(movimientos, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'movimientos': page_obj,
        'page_obj': page_obj,
        'material_filtro': material_filtro,
        'tipo_filtro': tipo_filtro,
        'motivo_filtro': motivo_filtro,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'materiales': Material.objects.filter(activo=True).order_by('nombre'),
        'tipos_movimiento': MovimientoMaterial.TIPO_MOVIMIENTO_CHOICES,
        'motivos': MovimientoMaterial.MOTIVO_CHOICES,
        'titulo': 'Movimientos de Materiales',
    }
    
    return render(request, 'sistema_interno/movimientos.html', context)

@login_required
def stock_critico_view(request):
    """Vista para análisis de stock crítico de materiales"""
    
    # Filtros
    categoria_filtro = request.GET.get('categoria', '')
    criticidad_filtro = request.GET.get('criticidad', '')
    tipo_alerta = request.GET.get('tipo_alerta', '')
    
    # Query base
    materiales = Material.objects.select_related('categoria', 'proveedor_principal').filter(activo=True)
    
    # Aplicar filtros
    if categoria_filtro:
        materiales = materiales.filter(categoria_id=categoria_filtro)
    
    if criticidad_filtro:
        materiales = materiales.filter(criticidad=criticidad_filtro)
    
    # Análisis de stock crítico
    materiales_agotados = materiales.filter(stock_actual=0)
    materiales_bajo_minimo = materiales.filter(stock_actual__lt=F('stock_minimo')).exclude(stock_minimo=0)
    materiales_cerca_reorden = materiales.filter(stock_actual__lte=F('punto_reorden'), stock_actual__gt=0)
    materiales_criticos = materiales.filter(criticidad='critica', stock_actual__lte=F('stock_minimo'))
    
    # Filtro por tipo de alerta
    if tipo_alerta == 'agotado':
        materiales_filtrados = materiales_agotados
    elif tipo_alerta == 'bajo_minimo':
        materiales_filtrados = materiales_bajo_minimo
    elif tipo_alerta == 'cerca_reorden':
        materiales_filtrados = materiales_cerca_reorden
    elif tipo_alerta == 'criticos':
        materiales_filtrados = materiales_criticos
    else:
        # Todos los materiales con algún tipo de alerta
        ids_alertas = (
            list(materiales_agotados.values_list('id', flat=True)) +
            list(materiales_bajo_minimo.values_list('id', flat=True)) +
            list(materiales_cerca_reorden.values_list('id', flat=True)) +
            list(materiales_criticos.values_list('id', flat=True))
        )
        materiales_filtrados = materiales.filter(id__in=ids_alertas)
    
    # Calcular métricas para cada material
    materiales_con_metricas = []
    for material in materiales_filtrados:
        # Determinar nivel de alerta
        if material.stock_actual <= 0:
            nivel_alerta = 'critico'
            tipo_alerta_material = 'Material Agotado'
        elif material.stock_actual < material.stock_minimo:
            nivel_alerta = 'alto'
            tipo_alerta_material = 'Stock Bajo'
        elif material.stock_actual <= material.punto_reorden:
            nivel_alerta = 'medio'
            tipo_alerta_material = 'Cerca de Reorden'
        else:
            nivel_alerta = 'normal'
            tipo_alerta_material = 'Normal'
        
        materiales_con_metricas.append({
            'material': material,
            'nivel_alerta': nivel_alerta,
            'tipo_alerta': tipo_alerta_material,
            'deficit': max(material.stock_minimo - material.stock_actual, 0),
            'valor_deficit': max(material.stock_minimo - material.stock_actual, 0) * material.precio_unitario,
            'dias_stock': (material.stock_actual / 1) if material.stock_actual > 0 else 0,  # Consumo estimado por día
        })
    
    # Estadísticas
    total_materiales = materiales.count()
    total_agotados = materiales_agotados.count()
    total_bajo_minimo = materiales_bajo_minimo.count()
    total_cerca_reorden = materiales_cerca_reorden.count()
    total_criticos = materiales_criticos.count()
    
    # Valor total en riesgo
    valor_total_riesgo = sum(item['valor_deficit'] for item in materiales_con_metricas)
    
    context = {
        'materiales_criticos': materiales_con_metricas,
        'total_materiales': total_materiales,
        'total_agotados': total_agotados,
        'total_bajo_minimo': total_bajo_minimo,
        'total_cerca_reorden': total_cerca_reorden,
        'total_criticos': total_criticos,
        'valor_total_riesgo': valor_total_riesgo,
        'categoria_filtro': categoria_filtro,
        'criticidad_filtro': criticidad_filtro,
        'tipo_alerta': tipo_alerta,
        'categorias': CategoriaMaterial.objects.filter(activo=True),
        'criticidades': Material.CRITICIDAD_CHOICES,
        'titulo': 'Stock Crítico - Materiales',
    }
    
    return render(request, 'sistema_interno/stock_critico.html', context)

@login_required
def proveedores_view(request):
    """Vista para gestión de proveedores - redirige al módulo de inventario"""
    return redirect('inventario:proveedores')

@login_required
def eliminar_material_view(request, pk):
    """Vista para eliminar material"""
    
    material = get_object_or_404(Material, pk=pk)
    
    if request.method == 'POST':
        nombre = material.nombre
        codigo = material.codigo
        material.delete()
        messages.success(
            request, 
            f'✅ Material "{codigo} - {nombre}" eliminado exitosamente.'
        )
        return redirect('materiales:materiales')
    
    context = {
        'material': material,
        'titulo': f'Eliminar Material - {material.codigo}',
    }
    
    return render(request, 'sistema_interno/confirmar_eliminar_material.html', context)

@login_required
def exportar_excel_view(request):
    """Vista para exportar materiales a Excel"""
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    from django.http import HttpResponse
    from datetime import date
    
    # Obtener los mismos filtros que la vista principal
    search_query = request.GET.get('search', '')
    categoria_filtro = request.GET.get('categoria', '')
    estado_filtro = request.GET.get('estado', '')
    criticidad_filtro = request.GET.get('criticidad', '')
    proveedor_filtro = request.GET.get('proveedor', '')
    tipo_filtro = request.GET.get('tipo', '')
    
    # Query base con los mismos filtros
    materiales = Material.objects.select_related('categoria', 'proveedor_principal').all()
    
    # Aplicar filtros
    if search_query:
        materiales = materiales.filter(
            Q(codigo__icontains=search_query) |
            Q(nombre__icontains=search_query) |
            Q(descripcion__icontains=search_query) |
            Q(marca__icontains=search_query) |
            Q(modelo__icontains=search_query)
        )
    
    if categoria_filtro:
        materiales = materiales.filter(categoria_id=categoria_filtro)
    
    if estado_filtro:
        materiales = materiales.filter(estado=estado_filtro)
    
    if criticidad_filtro:
        materiales = materiales.filter(criticidad=criticidad_filtro)
    
    if proveedor_filtro:
        materiales = materiales.filter(proveedor_principal_id=proveedor_filtro)
    
    if tipo_filtro:
        materiales = materiales.filter(tipo=tipo_filtro)
    
    # Crear workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Inventario de Materiales"
    
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
        'Código', 'Nombre', 'Descripción', 'Tipo', 'Categoría', 'Marca',
        'Modelo', 'Stock Actual', 'Stock Mínimo', 'Stock Máximo', 
        'Punto Reorden', 'Unidad', 'Precio Unitario', 'Valor Total',
        'Estado', 'Criticidad', 'Proveedor', 'Ubicación',
        'Fecha Vencimiento', 'Requiere Refrigeración', 'Manejo Especial'
    ]
    
    # Escribir encabezados con estilo
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center_alignment
        cell.border = border
    
    # Escribir datos
    for row_num, material in enumerate(materiales, 2):
        valor_total = material.valor_stock_actual()
        
        data = [
            material.codigo,
            material.nombre,
            material.descripcion,
            material.get_tipo_display(),
            material.categoria.nombre if material.categoria else '',
            material.marca or '',
            material.modelo or '',
            float(material.stock_actual),
            float(material.stock_minimo),
            float(material.stock_maximo),
            float(material.punto_reorden),
            material.get_unidad_medida_display(),
            float(material.precio_unitario),
            float(valor_total),
            material.get_estado_display(),
            material.get_criticidad_display(),
            material.proveedor_principal.nombre if material.proveedor_principal else '',
            material.ubicacion or '',
            material.fecha_vencimiento if material.fecha_vencimiento else '',
            'Sí' if material.requiere_refrigeracion else 'No',
            'Sí' if material.requiere_manejo_especial else 'No'
        ]
        
        for col, value in enumerate(data, 1):
            cell = ws.cell(row=row_num, column=col, value=value)
            cell.border = border
            
            # Formato especial para números
            if col in [8, 9, 10, 11, 13, 14]:  # Columnas numéricas
                cell.alignment = Alignment(horizontal='right')
            else:
                cell.alignment = Alignment(horizontal='left')
    
    # Ajustar ancho de columnas
    for col in range(1, len(headers) + 1):
        column_letter = get_column_letter(col)
        if col in [3]:  # Descripción
            ws.column_dimensions[column_letter].width = 40
        elif col in [1, 2, 4, 5, 17, 18]:  # Códigos, nombres, etc.
            ws.column_dimensions[column_letter].width = 20
        elif col in [6, 7]:  # Marca, modelo
            ws.column_dimensions[column_letter].width = 15
        else:
            ws.column_dimensions[column_letter].width = 12
    
    # Crear respuesta HTTP
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="inventario_materiales_{date.today().strftime("%Y%m%d")}.xlsx"'
    
    wb.save(response)
    return response

@login_required
def exportar_pdf_view(request):
    """Vista para exportar materiales a PDF"""
    from django.http import HttpResponse
    from django.template.loader import render_to_string
    from weasyprint import HTML
    from datetime import date
    
    # Obtener los mismos filtros que la vista principal
    search_query = request.GET.get('search', '')
    categoria_filtro = request.GET.get('categoria', '')
    estado_filtro = request.GET.get('estado', '')
    
    # Query base con filtros
    materiales = Material.objects.select_related('categoria', 'proveedor_principal').all()
    
    # Aplicar filtros básicos
    if search_query:
        materiales = materiales.filter(
            Q(codigo__icontains=search_query) |
            Q(nombre__icontains=search_query)
        )
    
    if categoria_filtro:
        materiales = materiales.filter(categoria_id=categoria_filtro)
    
    if estado_filtro:
        materiales = materiales.filter(estado=estado_filtro)
    
    # Limitar a 100 materiales para el PDF
    materiales = materiales[:100]
    
    # Calcular estadísticas
    total_materiales = materiales.count()
    valor_total = sum(m.valor_stock_actual() for m in materiales)
    
    # Renderizar HTML
    html_string = render_to_string('sistema_interno/materiales_pdf_template.html', {
        'materiales': materiales,
        'total_materiales': total_materiales,
        'valor_total': valor_total,
        'fecha_generacion': timezone.now(),
        'search_query': search_query,
        'categoria_filtro': categoria_filtro,
        'estado_filtro': estado_filtro,
    })
    
    # Convertir a PDF
    html = HTML(string=html_string)
    pdf = html.write_pdf()
    
    # Respuesta HTTP
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="inventario_materiales_{date.today().strftime("%Y%m%d")}.pdf"'
    
    return response

@login_required
def exportar_csv_view(request):
    """Vista para exportar materiales a CSV"""
    import csv
    from django.http import HttpResponse
    from datetime import date
    
    # Obtener filtros
    search_query = request.GET.get('search', '')
    categoria_filtro = request.GET.get('categoria', '')
    
    # Query base
    materiales = Material.objects.select_related('categoria', 'proveedor_principal').all()
    
    # Aplicar filtros básicos
    if search_query:
        materiales = materiales.filter(
            Q(codigo__icontains=search_query) |
            Q(nombre__icontains=search_query)
        )
    
    if categoria_filtro:
        materiales = materiales.filter(categoria_id=categoria_filtro)
    
    # Crear respuesta CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="inventario_materiales_{date.today().strftime("%Y%m%d")}.csv"'
    
    # Agregar BOM para UTF-8
    response.write('\ufeff')
    
    writer = csv.writer(response)
    
    # Escribir encabezados
    headers = [
        'Código', 'Nombre', 'Descripción', 'Tipo', 'Categoría', 'Marca',
        'Stock Actual', 'Stock Mínimo', 'Unidad Medida', 'Precio Unitario',
        'Estado', 'Criticidad', 'Proveedor Principal', 'Ubicación'
    ]
    writer.writerow(headers)
    
    # Escribir datos
    for material in materiales:
        row = [
            material.codigo,
            material.nombre,
            material.descripcion,
            material.get_tipo_display(),
            material.categoria.nombre if material.categoria else '',
            material.marca or '',
            float(material.stock_actual),
            float(material.stock_minimo),
            material.get_unidad_medida_display(),
            float(material.precio_unitario),
            material.get_estado_display(),
            material.get_criticidad_display(),
            material.proveedor_principal.nombre if material.proveedor_principal else '',
            material.ubicacion or ''
        ]
        writer.writerow(row)
    
    return response

@login_required
def crear_movimiento_view(request, pk):
    """Vista para crear movimiento de material específico"""
    
    material = get_object_or_404(Material, pk=pk)
    
    if request.method == 'POST':
        print(f"DEBUG MOVIMIENTO: POST recibido - datos: {request.POST}")  # Debug
        
        # Obtener datos del formulario
        tipo_movimiento = request.POST.get('tipo_movimiento')
        cantidad = request.POST.get('cantidad')
        motivo = request.POST.get('motivo', 'uso_proyecto')
        observaciones = request.POST.get('observaciones', '')
        costo_unitario = request.POST.get('costo_unitario', material.precio_unitario)
        
        try:
            # CAMBIAR: Convertir todo a Decimal en lugar de float
            cantidad = Decimal(str(cantidad)) if cantidad else Decimal('0')
            costo_unitario = Decimal(str(costo_unitario)) if costo_unitario else Decimal('0')
            
            # Validar datos
            if cantidad <= 0:
                messages.error(request, 'La cantidad debe ser mayor a cero.')
                return redirect(request.path)
            
            # Calcular nuevo stock - USAR SOLO Decimal
            stock_anterior = material.stock_actual  # Ya es Decimal
            
            if tipo_movimiento == 'entrada':
                stock_nuevo = stock_anterior + cantidad  # Decimal + Decimal
            elif tipo_movimiento == 'salida':
                if cantidad > stock_anterior:
                    messages.error(request, f'No hay suficiente stock. Stock actual: {stock_anterior}')
                    return redirect(request.path)
                stock_nuevo = stock_anterior - cantidad  # Decimal - Decimal
            elif tipo_movimiento == 'ajuste_positivo':
                stock_nuevo = stock_anterior + cantidad  # Decimal + Decimal
            elif tipo_movimiento == 'ajuste_negativo':
                stock_nuevo = stock_anterior - cantidad  # Decimal - Decimal
                if stock_nuevo < 0:
                    stock_nuevo = Decimal('0')  # Asegurar que sea Decimal
            else:
                messages.error(request, 'Tipo de movimiento no válido.')
                return redirect(request.path)
            
            # Crear el movimiento
            movimiento = MovimientoMaterial.objects.create(
                material=material,
                tipo_movimiento=tipo_movimiento,
                motivo=motivo,
                cantidad=cantidad,
                stock_anterior=stock_anterior,
                stock_nuevo=stock_nuevo,
                costo_unitario=costo_unitario,
                costo_total=cantidad * costo_unitario,  # Decimal * Decimal
                usuario=request.user,
                observaciones=observaciones,
                estado='procesado'
            )
            
            # Actualizar stock del material
            material.stock_actual = stock_nuevo
            material.save()  # Esto activará la actualización del estado
            
            messages.success(
                request, 
                f'✅ Movimiento registrado exitosamente. Nuevo stock: {stock_nuevo} {material.get_unidad_medida_display()}'
            )
            
            return redirect('materiales:material-detalle', pk=material.pk)
            
        except ValueError as e:
            print(f"DEBUG MOVIMIENTO: Error de valor - {e}")  # Debug
            messages.error(request, 'Error en los datos numéricos. Verifique que cantidad y costo sean números válidos.')
        except Exception as e:
            print(f"DEBUG MOVIMIENTO: Error general - {e}")  # Debug
            messages.error(request, f'Error al procesar el movimiento: {str(e)}')
    
    # Obtener datos para el contexto
    movimientos_recientes = MovimientoMaterial.objects.filter(
        material=material
    ).order_by('-fecha_movimiento')[:5]
    
    context = {
        'material': material,
        'movimientos_recientes': movimientos_recientes,
        'titulo': f'Crear Movimiento - {material.codigo}',
        'tipos_movimiento': MovimientoMaterial.TIPO_MOVIMIENTO_CHOICES,
        'motivos': MovimientoMaterial.MOTIVO_CHOICES,
    }
    
    return render(request, 'sistema_interno/crear_movimiento_material.html', context)