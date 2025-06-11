from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg, Max, Min
from datetime import datetime, timedelta
from .models import ProcedimientoOperativo, AnalisisRiesgo, MedidaControl
from .forms import ProcedimientoOperativoForm
from apps.equipos.models import Equipo
from django.utils import timezone
import json
import random

# AGREGAR ESTAS IMPORTACIONES:
from apps.materiales.models import MovimientoMaterial, Material
from apps.inventario.models import MovimientoStock, Repuesto

@login_required
def procedimientos_pop_view(request):
    """Vista principal de Procedimientos Operativos Estándar (POP)"""
    
    # Filtros
    search_query = request.GET.get('search', '')
    area_filtro = request.GET.get('area', '')
    estado_filtro = request.GET.get('estado', '')
    prioridad_filtro = request.GET.get('prioridad', '')
    tipo_filtro = request.GET.get('tipo', '')
    responsable_filtro = request.GET.get('responsable', '')
    equipo_filtro = request.GET.get('equipo', '')
    normativa_filtro = request.GET.get('normativa', '')
    
    # Query base
    procedimientos = ProcedimientoOperativo.objects.all()
    
    # Aplicar filtros
    if search_query:
        procedimientos = procedimientos.filter(
            Q(codigo__icontains=search_query) |
            Q(titulo__icontains=search_query) |
            Q(descripcion__icontains=search_query) |
            Q(responsable__icontains=search_query) |
            Q(equipo_asociado__icontains=search_query) |
            Q(normativa__icontains=search_query)
        )
    
    if area_filtro:
        procedimientos = procedimientos.filter(area=area_filtro)
    if estado_filtro:
        procedimientos = procedimientos.filter(estado=estado_filtro)
    if prioridad_filtro:
        procedimientos = procedimientos.filter(prioridad=prioridad_filtro)
    if tipo_filtro:
        procedimientos = procedimientos.filter(tipo=tipo_filtro)
    if responsable_filtro:
        procedimientos = procedimientos.filter(responsable=responsable_filtro)
    if equipo_filtro:
        procedimientos = procedimientos.filter(equipo_asociado__icontains=equipo_filtro)
    if normativa_filtro:
        procedimientos = procedimientos.filter(normativa__icontains=normativa_filtro)
    
    # Calcular estadísticas dinámicas
    total_pops = procedimientos.count()
    pops_activos = procedimientos.filter(estado='activo').count()
    pops_revision = procedimientos.filter(estado__in=['pendiente_aprobacion', 'en_capacitacion']).count()
    pops_criticos = procedimientos.filter(es_critico=True).count()
    pops_vencidos = procedimientos.filter(estado='vencido').count()
    
    # POPs próximos a vencer (30 días)
    fecha_limite = datetime.now().date() + timedelta(days=30)
    pops_proximos_vencer = procedimientos.filter(
        fecha_vencimiento__lte=fecha_limite,
        estado__in=['activo', 'validado_campo']
    ).count()
    
    # Calcular cumplimiento
    if total_pops > 0:
        cumplimiento = round(((pops_activos + pops_revision) / total_pops) * 100, 1)
    else:
        cumplimiento = 100
    
    # Obtener listas únicas para filtros
    responsables_disponibles = list(procedimientos.values_list('responsable', flat=True).distinct())
    equipos_disponibles = list(procedimientos.values_list('equipo_asociado', flat=True).distinct())
    normativas_disponibles = list(procedimientos.values_list('normativa', flat=True).distinct())
    
    # Obtener equipos del inventario
    equipos_inventario = Equipo.objects.filter(estado='OPERATIVO').order_by('codigo_interno')
    
    context = {
        'procedimientos': procedimientos,
        'search_query': search_query,
        'area_filtro': area_filtro,
        'estado_filtro': estado_filtro,
        'prioridad_filtro': prioridad_filtro,
        'tipo_filtro': tipo_filtro,
        'responsable_filtro': responsable_filtro,
        'equipo_filtro': equipo_filtro,
        'normativa_filtro': normativa_filtro,
        
        # Estadísticas
        'total_pops': total_pops,
        'pops_activos': pops_activos,
        'pops_revision': pops_revision,
        'pops_criticos': pops_criticos,
        'pops_vencidos': pops_vencidos,
        'pops_proximos_vencer': pops_proximos_vencer,
        'cumplimiento': cumplimiento,
        
        # Listas para filtros
        'responsables_disponibles': sorted([r for r in responsables_disponibles if r]),
        'equipos_disponibles': sorted([e for e in equipos_disponibles if e]),
        'normativas_disponibles': sorted([n for n in normativas_disponibles if n]),
        'equipos_inventario': equipos_inventario,
    }
    
    return render(request, 'sistema_interno/POP.html', context)

@login_required
def crear_pop_view(request):
    """Vista para crear nuevo procedimiento POP"""
    
    if request.method == 'POST':
        print(f"DEBUG: POST recibido - datos: {request.POST}")  # Debug
        form = ProcedimientoOperativoForm(request.POST, request.FILES)
        
        print(f"DEBUG: Form errors: {form.errors}")  # Debug
        print(f"DEBUG: Form is valid: {form.is_valid()}")  # Debug
        
        if form.is_valid():
            try:
                procedimiento = form.save(commit=False)
                procedimiento.creado_por = request.user
                
                # El código se genera automáticamente en el modelo
                # Manejar el action (draft o save)
                action = request.POST.get('action', 'save')
                if action == 'draft':
                    procedimiento.estado = 'pendiente_aprobacion'
                    messages.success(
                        request, 
                        f'✅ Borrador guardado: "{procedimiento.titulo}" - Código: {procedimiento.codigo}'
                    )
                else:
                    procedimiento.estado = 'pendiente_aprobacion'
                    messages.success(
                        request, 
                        f'✅ Procedimiento creado exitosamente: "{procedimiento.titulo}" - Código: {procedimiento.codigo}'
                    )
                
                procedimiento.save()
                
                return redirect('operaciones:procedimientos-pop')
                
            except Exception as e:
                print(f"DEBUG: Error al guardar: {str(e)}")  # Debug
                messages.error(
                    request, 
                    f'❌ Error al crear el procedimiento: {str(e)}'
                )
        else:
            print(f"DEBUG: Errores detallados del formulario:")
            for field, errors in form.errors.items():
                print(f"  - {field}: {errors}")
            
            # Crear mensaje de error más específico
            error_fields = []
            for field, errors in form.errors.items():
                if field == '__all__':
                    continue
                field_name = form.fields[field].label or field
                error_fields.append(f"{field_name}: {', '.join(errors)}")
            
            if error_fields:
                messages.error(
                    request, 
                    f'❌ Errores en el formulario:\n' + '\n'.join(error_fields)
                )
            else:
                messages.error(
                    request, 
                    '❌ Error en el formulario. Por favor revise los campos marcados en rojo.'
                )
    else:
        form = ProcedimientoOperativoForm()
    
    # Estadísticas para el contexto
    stats = {
        'total_pops': ProcedimientoOperativo.objects.count(),
        'total_equipos': Equipo.objects.exclude(estado='FUERA_SERVICIO').count(),
        'pops_activos': ProcedimientoOperativo.objects.filter(estado='activo').count(),
    }
    
    context = {
        'form': form,
        'accion': 'crear',
        'titulo': 'Crear Procedimiento Operativo Estándar',
        'stats': stats,
    }
    
    return render(request, 'sistema_interno/crear_pop.html', context)

@login_required
def editar_pop_view(request, codigo):
    """Vista para editar procedimiento POP existente"""
    
    procedimiento = get_object_or_404(ProcedimientoOperativo, codigo=codigo)
    
    if request.method == 'POST':
        print(f"DEBUG EDITAR: POST recibido - datos: {request.POST}")  # Debug
        print(f"DEBUG EDITAR: FILES recibidos: {request.FILES}")  # Debug
        
        form = ProcedimientoOperativoForm(request.POST, request.FILES, instance=procedimiento)
        
        print(f"DEBUG EDITAR: Form errors: {form.errors}")  # Debug
        print(f"DEBUG EDITAR: Form is valid: {form.is_valid()}")  # Debug
        
        if form.is_valid():
            try:
                print(f"DEBUG EDITAR: Datos válidos, guardando...")  # Debug
                procedimiento_actualizado = form.save()
                
                print(f"DEBUG EDITAR: Procedimiento guardado exitosamente: {procedimiento_actualizado.codigo}")  # Debug
                
                messages.success(
                    request, 
                    f'✅ Procedimiento "{procedimiento_actualizado.codigo} - {procedimiento_actualizado.titulo}" actualizado exitosamente.'
                )
                
                return redirect('operaciones:procedimientos-pop')
                
            except Exception as e:
                print(f"DEBUG EDITAR: Error al guardar: {str(e)}")  # Debug
                messages.error(
                    request, 
                    f'❌ Error al actualizar el procedimiento: {str(e)}'
                )
        else:
            print(f"DEBUG EDITAR: Errores detallados del formulario:")
            for field, errors in form.errors.items():
                print(f"  - {field}: {errors}")
            
            # Crear mensaje de error específico
            error_fields = []
            for field, errors in form.errors.items():
                if field == '__all__':
                    continue
                field_name = form.fields[field].label or field
                error_fields.append(f"{field_name}: {', '.join(errors)}")
            
            if error_fields:
                error_message = '❌ Errores en el formulario:\n' + '\n'.join(error_fields)
                messages.error(request, error_message)
            else:
                messages.error(
                    request, 
                    '❌ Error en el formulario. Por favor revise los campos marcados en rojo.'
                )
    else:
        print(f"DEBUG EDITAR: GET request - Cargando formulario para {procedimiento.codigo}")  # Debug
        form = ProcedimientoOperativoForm(instance=procedimiento)
    
    context = {
        'form': form,
        'procedimiento': procedimiento,
        'accion': 'editar',
        'titulo': f'Editar Procedimiento - {procedimiento.codigo}',
    }
    
    return render(request, 'sistema_interno/editar_pop.html', context)

@login_required
def ver_pop_view(request, codigo):
    """Vista detallada del procedimiento POP"""
    
    procedimiento = get_object_or_404(ProcedimientoOperativo, codigo=codigo)
    
    # Calcular métricas adicionales
    dias_restantes = procedimiento.dias_hasta_vencimiento()
    procedimiento.dias_restantes = dias_restantes
    procedimiento.dias_restantes_abs = abs(dias_restantes) if dias_restantes is not None else 0
    procedimiento.vencido = procedimiento.esta_vencido()
    
    context = {
        'procedimiento': procedimiento,
    }
    
    return render(request, 'sistema_interno/detalle_pop.html', context)

@login_required
def eliminar_pop_view(request, codigo):
    """Vista para eliminar procedimiento POP"""
    
    procedimiento = get_object_or_404(ProcedimientoOperativo, codigo=codigo)
    
    if request.method == 'POST':
        titulo = procedimiento.titulo
        procedimiento.delete()
        messages.success(request, f'Procedimiento "{titulo}" eliminado exitosamente.')
        return redirect('operaciones:procedimientos-pop')
    
    context = {
        'procedimiento': procedimiento,
    }
    
    return render(request, 'sistema_interno/confirmar_eliminar_pop.html', context)

@login_required
def aprobar_pop_view(request, codigo):
    """Vista para aprobar procedimiento POP"""
    
    procedimiento = get_object_or_404(ProcedimientoOperativo, codigo=codigo)
    
    if request.method == 'POST':
        procedimiento.estado = 'activo'
        procedimiento.aprobado_por = request.user
        procedimiento.fecha_aprobacion = datetime.now()
        procedimiento.save()
        
        messages.success(
            request, 
            f'✅ Procedimiento "{procedimiento.codigo}" aprobado exitosamente.'
        )
        return redirect('operaciones:procedimientos-pop')
    
    context = {
        'procedimiento': procedimiento,
    }
    
    return render(request, 'sistema_interno/aprobar_pop.html', context)

@login_required
def renovar_pop_view(request, codigo):
    """Vista para renovar procedimiento POP vencido"""
    
    procedimiento = get_object_or_404(ProcedimientoOperativo, codigo=codigo)
    
    if request.method == 'POST':
        # Actualizar fechas
        nueva_fecha_revision = datetime.now().date()
        nueva_fecha_vencimiento = nueva_fecha_revision + timedelta(days=365)
        
        procedimiento.fecha_ultima_revision = nueva_fecha_revision
        procedimiento.fecha_proxima_revision = nueva_fecha_vencimiento
        procedimiento.fecha_vencimiento = nueva_fecha_vencimiento
        procedimiento.estado = 'activo'
        
        # Incrementar versión
        version_actual = procedimiento.version
        if version_actual.startswith('v'):
            try:
                numero = float(version_actual[1:])
                nueva_version = f"v{numero + 0.1:.1f}"
            except:
                nueva_version = "v1.1"
        else:
            nueva_version = "v1.1"
        
        procedimiento.version = nueva_version
        procedimiento.save()
        
        messages.success(
            request, 
            f'✅ Procedimiento "{procedimiento.codigo}" renovado exitosamente. Nueva versión: {nueva_version}'
        )
        return redirect('operaciones:procedimientos-pop')
    
    context = {
        'procedimiento': procedimiento,
    }
    
    return render(request, 'sistema_interno/renovar_pop.html', context)

@login_required
def descargar_pop_pdf_view(request, codigo):
    """Vista para descargar procedimiento POP en PDF"""
    
    from django.http import HttpResponse
    from django.template.loader import render_to_string
    from weasyprint import HTML
    
    procedimiento = get_object_or_404(ProcedimientoOperativo, codigo=codigo)
    
    # Renderizar HTML
    html_string = render_to_string('sistema_interno/pop_pdf_template.html', {
        'procedimiento': procedimiento,
    })
    
    # Convertir a PDF
    html = HTML(string=html_string)
    pdf = html.write_pdf()
    
    # Respuesta HTTP
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="POP_{procedimiento.codigo}.pdf"'
    
    return response

@login_required
def analisis_riesgos_view(request):
    """Vista de Análisis de Riesgos Industrial - Sistema de Gestión de Riesgos"""
    
    # Obtener todos los riesgos de la base de datos
    riesgos_queryset = AnalisisRiesgo.objects.select_related('equipo_asociado', 'identificado_por').all()
    
    # === ESTADÍSTICAS REALES ===
    total_riesgos = riesgos_queryset.count()
    riesgos_extremos = riesgos_queryset.filter(nivel_riesgo='extremo').count()
    riesgos_altos = riesgos_queryset.filter(nivel_riesgo='alto').count()
    riesgos_medios = riesgos_queryset.filter(nivel_riesgo='medio').count()
    riesgos_bajos = riesgos_queryset.filter(nivel_riesgo='bajo').count()
    riesgos_triviales = riesgos_queryset.filter(nivel_riesgo='trivial').count()
    
    # Porcentaje de riesgos controlados
    riesgos_controlados = riesgos_queryset.filter(estado='controlado').count()
    porcentaje_controlados = (riesgos_controlados / total_riesgos * 100) if total_riesgos > 0 else 0
    
    # === ANÁLISIS POR ÁREA ===
    areas_planta = [
        'soldadura', 'maquinado', 'fundicion', 'calidad', 
        'mantenimiento', 'almacen', 'oficinas', 'laboratorio'
    ]
    
    riesgos_por_area = {}
    for area in areas_planta:
        riesgos_area = riesgos_queryset.filter(area=area)
        if riesgos_area.exists():
            stats = riesgos_area.aggregate(
                promedio=Avg('riesgo_actual'),
                maximo=Max('riesgo_actual'),
                minimo=Min('riesgo_actual')
            )
            
            def clasificar_nivel(valor):
                if valor >= 20: return 'Extremo'
                elif valor >= 15: return 'Alto'
                elif valor >= 10: return 'Medio'
                elif valor >= 5: return 'Bajo'
                else: return 'Trivial'
            
            riesgos_por_area[area.title()] = {
                'total': riesgos_area.count(),
                'promedio': round(stats['promedio'], 1) if stats['promedio'] else 0,
                'maximo': stats['maximo'] if stats['maximo'] else 0,
                'minimo': stats['minimo'] if stats['minimo'] else 0,
                'nivel': clasificar_nivel(stats['promedio'] if stats['promedio'] else 0),
                'controlados': riesgos_area.filter(estado='controlado').count(),
                'en_tratamiento': riesgos_area.filter(estado='en_tratamiento').count(),
                'extremos': riesgos_area.filter(nivel_riesgo='extremo').count(),
                'altos': riesgos_area.filter(nivel_riesgo='alto').count(),
            }
    
    # === TENDENCIAS TEMPORALES (últimos 6 meses) ===
    meses_labels = []
    riesgos_identificados_mes = []
    riesgos_mitigados_mes = []
    
    for i in range(6):
        mes = timezone.now() - timedelta(days=30*i)  # <- mes ya es timezone-aware
        meses_labels.insert(0, mes.strftime('%b'))
        
        # CAMBIAR ESTAS LÍNEAS - NO usar make_aware porque mes ya es aware:
        inicio_mes = mes.replace(day=1, hour=0, minute=0, second=0, microsecond=0)  # <- QUITAR timezone.make_aware
        if i == 0:
            fin_mes = timezone.now()
        else:
            siguiente_mes = inicio_mes + timedelta(days=32)
            fin_mes = siguiente_mes.replace(day=1) - timedelta(days=1)  # <- QUITAR timezone.make_aware
        
        identificados = riesgos_queryset.filter(
            fecha_identificacion__gte=inicio_mes.date(),
            fecha_identificacion__lte=fin_mes.date()
        ).count()
        
        # Riesgos que cambiaron a "controlado" en ese mes
        mitigados = riesgos_queryset.filter(
            fecha_actualizacion__gte=inicio_mes,
            fecha_actualizacion__lte=fin_mes,
            estado='controlado'
        ).count()
        
        riesgos_identificados_mes.insert(0, identificados)
        riesgos_mitigados_mes.insert(0, mitigados)
    
    # === PRÓXIMAS REVISIONES ===
    proximas_revisiones = riesgos_queryset.filter(
        fecha_revision__lte=datetime.now().date() + timedelta(days=30),
        estado__in=['identificado', 'en_tratamiento', 'en_revision']
    ).order_by('fecha_revision')[:5]
    
    # === ALERTAS Y RECOMENDACIONES ===
    alertas = []
    
    # Alertas por riesgos extremos
    if riesgos_extremos > 0:
        alertas.append({
            'tipo': 'danger',
            'titulo': f'{riesgos_extremos} Riesgo(s) Extremo(s) Identificado(s)',
            'descripcion': 'Requieren atención inmediata y medidas de control urgentes',
            'accion': 'Implementar medidas de control inmediatas'
        })
    
    # Alertas por revisiones vencidas
    revisiones_vencidas = riesgos_queryset.filter(
        fecha_revision__lt=datetime.now().date(),
        estado__in=['identificado', 'en_tratamiento', 'en_revision']
    ).count()
    
    if revisiones_vencidas > 0:
        alertas.append({
            'tipo': 'warning',
            'titulo': f'{revisiones_vencidas} Revisión(es) Vencida(s)',
            'descripcion': 'Riesgos que requieren revisión inmediata',
            'accion': 'Programar revisiones pendientes'
        })
    
    # Alerta por área con mayor riesgo
    if riesgos_por_area:
        area_mayor_riesgo = max(riesgos_por_area.items(), key=lambda x: x[1]['promedio'])
        if area_mayor_riesgo[1]['promedio'] >= 12:
            alertas.append({
                'tipo': 'info',
                'titulo': f'Área {area_mayor_riesgo[0]} requiere atención',
                'descripcion': f'Promedio de riesgo: {area_mayor_riesgo[1]["promedio"]}',
                'accion': 'Implementar plan de mejora específico'
            })
    
    # === FILTROS APLICADOS ===
    area_filtro = request.GET.get('area', '')
    tipo_filtro = request.GET.get('tipo', '')
    nivel_filtro = request.GET.get('nivel', '')
    estado_filtro = request.GET.get('estado', '')
    
    # Aplicar filtros
    riesgos_filtrados = riesgos_queryset
    
    if area_filtro:
        riesgos_filtrados = riesgos_filtrados.filter(area=area_filtro)
    
    if tipo_filtro:
        riesgos_filtrados = riesgos_filtrados.filter(tipo=tipo_filtro)
    
    if nivel_filtro:
        riesgos_filtrados = riesgos_filtrados.filter(nivel_riesgo=nivel_filtro)
    
    if estado_filtro:
        riesgos_filtrados = riesgos_filtrados.filter(estado=estado_filtro)
    
    # Ordenar por nivel de riesgo (descendente)
    riesgos_filtrados = riesgos_filtrados.order_by('-riesgo_actual', '-fecha_creacion')
    
    # === INDICADORES DE DESEMPEÑO ===
    # Calcular métricas reales si hay datos suficientes
    if total_riesgos > 0:
        # Tiempo promedio de resolución (riesgos controlados)
        riesgos_resueltos = riesgos_queryset.filter(estado='controlado')
        if riesgos_resueltos.exists():
            tiempos_resolucion = []
            for riesgo in riesgos_resueltos:
                if riesgo.fecha_ultima_revision:
                    dias = (riesgo.fecha_ultima_revision - riesgo.fecha_identificacion).days
                    tiempos_resolucion.append(dias)
            
            dias_promedio_resolucion = sum(tiempos_resolucion) / len(tiempos_resolucion) if tiempos_resolucion else 30
        else:
            dias_promedio_resolucion = 30
        
        # Eficacia de controles (porcentaje de riesgos controlados)
        eficacia_controles = porcentaje_controlados
        
        # Cumplimiento de revisiones
        total_con_revision = riesgos_queryset.exclude(fecha_revision__isnull=True).count()
        revisiones_al_dia = riesgos_queryset.filter(
            fecha_revision__gte=datetime.now().date()
        ).count()
        cumplimiento_revisiones = (revisiones_al_dia / total_con_revision * 100) if total_con_revision > 0 else 100
    else:
        # Valores por defecto si no hay datos
        dias_promedio_resolucion = 0
        eficacia_controles = 0
        cumplimiento_revisiones = 100
    
    # Convertir QuerySet a lista de diccionarios para el template
    riesgos_para_template = []
    for riesgo in riesgos_filtrados[:20]:  # Limitar a 20 para performance
        riesgo_dict = {
            'codigo': riesgo.codigo,
            'descripcion': riesgo.descripcion,
            'area': riesgo.get_area_display(),
            'tipo': riesgo.get_tipo_display(),
            'probabilidad': riesgo.probabilidad,
            'severidad': riesgo.severidad,
            'riesgo_actual': riesgo.riesgo_actual,
            'nivel': riesgo.nivel_riesgo.title(),
            'color': riesgo.get_color_riesgo(),
            'estado': riesgo.get_estado_display(),
            'responsable': riesgo.responsable,
            'fecha_identificacion': riesgo.fecha_identificacion,
            'fecha_revision': riesgo.fecha_revision,
            'medidas_control': riesgo.medidas_control.split('\n') if riesgo.medidas_control else [],
        }
        riesgos_para_template.append(riesgo_dict)
    
    context = {
        # Datos principales
        'riesgos': riesgos_para_template,
        'todos_los_riesgos': riesgos_para_template,
        'proximas_revisiones': proximas_revisiones,
        'alertas': alertas,
        
        # Estadísticas generales
        'total_riesgos': total_riesgos,
        'riesgos_extremos': riesgos_extremos,
        'riesgos_altos': riesgos_altos,
        'riesgos_medios': riesgos_medios,
        'riesgos_controlados': riesgos_controlados,
        'porcentaje_controlados': round(porcentaje_controlados, 1),
        
        # Análisis por área
        'riesgos_por_area': riesgos_por_area,
        'area_mayor_riesgo': max(riesgos_por_area.items(), key=lambda x: x[1]['promedio']) if riesgos_por_area else None,
        
        # Indicadores de desempeño
        'dias_promedio_resolucion': round(dias_promedio_resolucion, 1),
        'eficacia_controles': round(eficacia_controles, 1),
        'cumplimiento_revisiones': round(cumplimiento_revisiones, 1),
        
        # Datos para gráficos (JSON)
        'meses_labels': json.dumps(meses_labels),
        'riesgos_identificados_data': json.dumps(riesgos_identificados_mes),
        'riesgos_mitigados_data': json.dumps(riesgos_mitigados_mes),
        
        # Filtros
        'area_filtro': area_filtro,
        'tipo_filtro': tipo_filtro,
        'nivel_filtro': nivel_filtro,
        'estado_filtro': estado_filtro,
        'areas_disponibles': [choice[1] for choice in AnalisisRiesgo.AREA_CHOICES],
        'tipos_disponibles': [choice[1] for choice in AnalisisRiesgo.TIPO_RIESGO_CHOICES],
        'niveles_disponibles': ['Extremo', 'Alto', 'Medio', 'Bajo', 'Trivial'],
        'estados_disponibles': [choice[1] for choice in AnalisisRiesgo.ESTADO_CHOICES],
        
        # Metadatos
        'fecha_actualizacion': datetime.now(),
    }
    
    return render(request, 'sistema_interno/analisis_riesgo.html', context)

@login_required
def movimientos_unificados_view(request):
    """Vista unificada de movimientos de materiales, repuestos y equipos"""
    
    # Filtros
    tipo_filtro = request.GET.get('tipo', '')  # material, repuesto, equipo
    movimiento_filtro = request.GET.get('movimiento', '')  # entrada, salida, etc.
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    search = request.GET.get('search', '')
    
    # === OBTENER MOVIMIENTOS DE MATERIALES ===
    movimientos_materiales = MovimientoMaterial.objects.select_related(
        'material', 'usuario'
    ).all()
    
    if tipo_filtro == 'material' or not tipo_filtro:
        if movimiento_filtro:
            movimientos_materiales = movimientos_materiales.filter(tipo_movimiento=movimiento_filtro)
        if search:
            movimientos_materiales = movimientos_materiales.filter(
                Q(material__nombre__icontains=search) |
                Q(material__codigo__icontains=search) |
                Q(numero_movimiento__icontains=search)
            )
        if fecha_desde:
            movimientos_materiales = movimientos_materiales.filter(fecha_movimiento__date__gte=fecha_desde)
        if fecha_hasta:
            movimientos_materiales = movimientos_materiales.filter(fecha_movimiento__date__lte=fecha_hasta)
    else:
        movimientos_materiales = MovimientoMaterial.objects.none()
    
    # === OBTENER MOVIMIENTOS DE REPUESTOS ===
    movimientos_repuestos = MovimientoStock.objects.select_related(
        'repuesto', 'usuario'
    ).all()
    
    if tipo_filtro == 'repuesto' or not tipo_filtro:
        if movimiento_filtro:
            movimientos_repuestos = movimientos_repuestos.filter(tipo_movimiento=movimiento_filtro)
        if search:
            movimientos_repuestos = movimientos_repuestos.filter(
                Q(repuesto__nombre__icontains=search) |
                Q(repuesto__codigo__icontains=search) |
                Q(numero_movimiento__icontains=search)
            )
        if fecha_desde:
            movimientos_repuestos = movimientos_repuestos.filter(fecha_movimiento__date__gte=fecha_desde)
        if fecha_hasta:
            movimientos_repuestos = movimientos_repuestos.filter(fecha_movimiento__date__lte=fecha_hasta)
    else:
        movimientos_repuestos = MovimientoStock.objects.none()
    
    # === CONVERTIR A LISTA UNIFICADA ===
    movimientos_unificados = []
    
    # Agregar movimientos de materiales
    for mov in movimientos_materiales:
        movimientos_unificados.append({
            'id': f"mat_{mov.id}",
            'numero': mov.numero_movimiento,
            'tipo_item': 'Material',
            'item_nombre': mov.material.nombre,
            'item_codigo': mov.material.codigo,
            'item_categoria': mov.material.categoria.nombre if mov.material.categoria else 'Sin categoría',
            'tipo_movimiento': mov.tipo_movimiento,
            'tipo_movimiento_display': mov.get_tipo_movimiento_display(),
            'motivo': mov.get_motivo_display(),
            'cantidad': mov.cantidad,
            'unidad': mov.material.get_unidad_medida_display(),
            'stock_anterior': mov.stock_anterior,
            'stock_nuevo': mov.stock_nuevo,
            'costo_unitario': mov.costo_unitario,
            'costo_total': mov.costo_total,
            'usuario': mov.usuario.get_full_name() if mov.usuario else 'Sistema',
            'fecha_movimiento': mov.fecha_movimiento,
            'observaciones': getattr(mov, 'observaciones', ''),  # Usar getattr para seguridad
            'estado': mov.get_estado_display(),
            'origen': 'materiales',
            'detalle_url': f"/materiales/detalle/{mov.material.pk}/",
        })
    
    # Agregar movimientos de repuestos
    for mov in movimientos_repuestos:
        movimientos_unificados.append({
            'id': f"rep_{mov.id}",
            'numero': getattr(mov, 'numero_movimiento', f'REP-{mov.id}'),  # Usar getattr
            'tipo_item': 'Repuesto',
            'item_nombre': mov.repuesto.nombre,
            'item_codigo': mov.repuesto.codigo,
            'item_categoria': mov.repuesto.categoria.nombre if mov.repuesto.categoria else 'Sin categoría',
            'tipo_movimiento': mov.tipo_movimiento,
            'tipo_movimiento_display': mov.get_tipo_movimiento_display(),
            'motivo': mov.get_motivo_display() if hasattr(mov, 'get_motivo_display') else 'N/A',
            'cantidad': mov.cantidad,
            'unidad': mov.repuesto.get_unidad_medida_display(),
            'stock_anterior': mov.stock_anterior,
            'stock_nuevo': mov.stock_nuevo,
            'costo_unitario': getattr(mov, 'costo_unitario', 0),
            'costo_total': getattr(mov, 'costo_total', 0),
            'usuario': mov.usuario.get_full_name() if mov.usuario else 'Sistema',
            'fecha_movimiento': mov.fecha_movimiento,
            'observaciones': getattr(mov, 'observaciones', getattr(mov, 'notas', '')),  # Intentar observaciones o notas
            'estado': mov.get_estado_display() if hasattr(mov, 'get_estado_display') else 'Procesado',
            'origen': 'inventario',
            'detalle_url': f"/inventario/repuesto/{mov.repuesto.pk}/",
        })
    
    # === ORDENAR POR FECHA (MÁS RECIENTES PRIMERO) ===
    movimientos_unificados.sort(key=lambda x: x['fecha_movimiento'], reverse=True)
    
    # === PAGINACIÓN MANUAL ===
    from django.core.paginator import Paginator
    paginator = Paginator(movimientos_unificados, 20)  # 20 movimientos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # === ESTADÍSTICAS ===
    total_movimientos = len(movimientos_unificados)
    entradas = sum(1 for mov in movimientos_unificados if mov['tipo_movimiento'] in ['entrada', 'ajuste_positivo'])
    salidas = sum(1 for mov in movimientos_unificados if mov['tipo_movimiento'] in ['salida', 'ajuste_negativo'])
    transferencias = sum(1 for mov in movimientos_unificados if 'transferencia' in mov['tipo_movimiento'])
    
    # Estadísticas por tipo
    movimientos_materiales_count = sum(1 for mov in movimientos_unificados if mov['origen'] == 'materiales')
    movimientos_repuestos_count = sum(1 for mov in movimientos_unificados if mov['origen'] == 'inventario')
    
    # Valor total movilizado
    valor_total = sum(mov['costo_total'] or 0 for mov in movimientos_unificados)
    
    # Obtener listas para filtros
    tipos_movimiento = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
        ('ajuste_positivo', 'Ajuste Positivo'),
        ('ajuste_negativo', 'Ajuste Negativo'),
        ('transferencia', 'Transferencia'),
        ('devolucion', 'Devolución'),
        ('merma', 'Merma'),
    ]
    
    context = {
        'movimientos': page_obj,
        'page_obj': page_obj,
        'total_movimientos': total_movimientos,
        'entradas': entradas,
        'salidas': salidas,
        'transferencias': transferencias,
        'movimientos_materiales': movimientos_materiales_count,
        'movimientos_repuestos': movimientos_repuestos_count,
        'valor_total': valor_total,
        'search': search,
        'tipo_filtro': tipo_filtro,
        'movimiento_filtro': movimiento_filtro,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'tipos_movimiento': tipos_movimiento,
        'titulo': 'Movimientos de Inventario',
        'fecha_actualizacion': timezone.now(),
    }
    
    return render(request, 'sistema_interno/movimientos_unificados.html', context)