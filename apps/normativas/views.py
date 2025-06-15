from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg, Sum
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.urls import reverse
from django.conf import settings
import os
import mimetypes

from .models import (
    NormativaSeguridad, CategoriaSeguridad, InspeccionSeguridad, 
    IncidenteSeguridad, HistorialNormativa, CapacitacionSeguridad, 
    ParticipacionCapacitacion
)
from .forms import (
    NormativaSeguridadForm, CategoriaSeguridadForm, FiltrosNormativasForm,
    InspeccionSeguridadForm, IncidenteSeguridadForm, CapacitacionSeguridadForm
)

def es_staff_o_admin(user):
    """Verifica si el usuario es staff o admin"""
    return user.is_authenticated and (user.is_staff or user.is_superuser)

@login_required
def normativas_view(request):
    """Vista principal del módulo de normativas y seguridad"""
    
    # Obtener filtros de la URL
    categoria_filtro = request.GET.get('categoria', '')
    tipo_filtro = request.GET.get('tipo', '')
    prioridad_filtro = request.GET.get('prioridad', '')
    ambito_filtro = request.GET.get('ambito', '')
    estado_filtro = request.GET.get('estado', 'vigente')  # Por defecto mostrar vigentes
    busqueda = request.GET.get('busqueda', '')
    
    # Query base - normativas vigentes
    normativas = NormativaSeguridad.objects.select_related(
        'categoria', 'autor', 'aprobado_por'
    ).order_by('-fecha_modificacion')
    
    # Aplicar filtros
    if estado_filtro:
        normativas = normativas.filter(estado=estado_filtro)
    
    if categoria_filtro:
        normativas = normativas.filter(categoria_id=categoria_filtro)
    
    if tipo_filtro:
        normativas = normativas.filter(tipo=tipo_filtro)
    
    if prioridad_filtro:
        normativas = normativas.filter(prioridad=prioridad_filtro)
    
    if ambito_filtro:
        normativas = normativas.filter(ambito_aplicacion=ambito_filtro)
    
    if busqueda:
        normativas = normativas.filter(
            Q(titulo__icontains=busqueda) |
            Q(descripcion__icontains=busqueda) |
            Q(codigo__icontains=busqueda) |
            Q(palabras_clave__icontains=busqueda)
        )
    
    # Estadísticas principales
    stats = {
        'total_normativas': NormativaSeguridad.objects.count(),
        'vigentes': NormativaSeguridad.objects.filter(estado='vigente').count(),
        'en_revision': NormativaSeguridad.objects.filter(estado='revision').count(),
        'por_revisar': NormativaSeguridad.objects.filter(
            proxima_revision__lte=timezone.now().date() + timezone.timedelta(days=30)
        ).count(),
        'criticas': NormativaSeguridad.objects.filter(
            prioridad='critica', estado='vigente'
        ).count(),
        'total_incidentes': IncidenteSeguridad.objects.count(),
        'incidentes_este_mes': IncidenteSeguridad.objects.filter(
            fecha_incidente__gte=timezone.now().replace(day=1)
        ).count(),
        'inspecciones_este_mes': InspeccionSeguridad.objects.filter(
            fecha_inspeccion__gte=timezone.now().replace(day=1)
        ).count(),
    }
    
    # Normativas más consultadas
    normativas_populares = NormativaSeguridad.objects.filter(
        estado='vigente'
    ).order_by('-vistas')[:6]
    
    # Normativas críticas
    normativas_criticas = NormativaSeguridad.objects.filter(
        estado='vigente',
        prioridad='critica'
    ).order_by('-fecha_modificacion')[:5]
    
    # Normativas que requieren revisión próxima
    normativas_revision = NormativaSeguridad.objects.filter(
        estado='vigente',
        proxima_revision__lte=timezone.now().date() + timezone.timedelta(days=30)
    ).order_by('proxima_revision')[:5]
    
    # Categorías con estadísticas
    categorias_stats = CategoriaSeguridad.objects.filter(
        activo=True
    ).annotate(
        total_normativas=Count('normativas', filter=Q(normativas__estado='vigente'))
    ).order_by('orden')
    
    # Incidentes recientes
    incidentes_recientes = IncidenteSeguridad.objects.select_related(
        'reportado_por'
    ).order_by('-fecha_incidente')[:5]
    
    # Inspecciones recientes
    inspecciones_recientes = InspeccionSeguridad.objects.select_related(
        'normativa', 'inspector'
    ).order_by('-fecha_inspeccion')[:5]
    
    # Capacitaciones programadas
    capacitaciones_proximas = CapacitacionSeguridad.objects.filter(
        estado__in=['programada', 'en_curso'],
        fecha_inicio__gte=timezone.now()
    ).order_by('fecha_inicio')[:5]
    
    # Paginación
    paginator = Paginator(normativas, 12)  # 12 normativas por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Alertas importantes
    alertas = []
    
    # Alertas de normativas que requieren revisión
    if stats['por_revisar'] > 0:
        alertas.append({
            'tipo': 'warning',
            'titulo': f'{stats["por_revisar"]} normativas requieren revisión',
            'mensaje': 'Hay normativas que vencen en los próximos 30 días',
            'fecha': timezone.now()
        })
    
    # Alertas de incidentes sin resolver
    incidentes_pendientes = IncidenteSeguridad.objects.filter(
        estado__in=['reportado', 'investigando']
    ).count()
    
    if incidentes_pendientes > 0:
        alertas.append({
            'tipo': 'critica',
            'titulo': f'{incidentes_pendientes} incidentes pendientes',
            'mensaje': 'Hay incidentes de seguridad sin resolver',
            'fecha': timezone.now()
        })
    
    # Alertas de inspecciones vencidas
    inspecciones_vencidas = InspeccionSeguridad.objects.filter(
        fecha_limite_correccion__lt=timezone.now().date(),
        corregido=False
    ).count()
    
    if inspecciones_vencidas > 0:
        alertas.append({
            'tipo': 'critica',
            'titulo': f'{inspecciones_vencidas} inspecciones vencidas',
            'mensaje': 'Hay observaciones de inspecciones sin corregir',
            'fecha': timezone.now()
        })
    
    context = {
        'normativas': page_obj,
        'page_obj': page_obj,
        'stats': stats,
        'normativas_populares': normativas_populares,
        'normativas_criticas': normativas_criticas,
        'normativas_revision': normativas_revision,
        'categorias_stats': categorias_stats,
        'incidentes_recientes': incidentes_recientes,
        'inspecciones_recientes': inspecciones_recientes,
        'capacitaciones_proximas': capacitaciones_proximas,
        'alertas': alertas,
        'es_admin': es_staff_o_admin(request.user),
        'categoria_filtro': categoria_filtro,
        'tipo_filtro': tipo_filtro,
        'prioridad_filtro': prioridad_filtro,
        'ambito_filtro': ambito_filtro,
        'estado_filtro': estado_filtro,
        'busqueda': busqueda,
        'categorias': CategoriaSeguridad.objects.filter(activo=True),
        'tipos': NormativaSeguridad.TIPO_CHOICES,
        'prioridades': NormativaSeguridad.PRIORIDAD_CHOICES,
        'ambitos': NormativaSeguridad.AMBITO_CHOICES,
        'estados': NormativaSeguridad.ESTADO_CHOICES,
    }
    
    return render(request, 'sistema_interno/normativas.html', context)

@login_required
def ver_normativa_view(request, normativa_id):
    """Vista para ver una normativa específica"""
    
    normativa = get_object_or_404(NormativaSeguridad, id=normativa_id)
    
    # Incrementar contador de vistas y registrar
    normativa.incrementar_vista(request.user)
    
    # Normativas relacionadas
    normativas_relacionadas = normativa.normativas_relacionadas.filter(
        estado='vigente'
    )[:4]
    
    # Si no hay relacionadas manuales, buscar por categoría
    if not normativas_relacionadas.exists():
        normativas_relacionadas = NormativaSeguridad.objects.filter(
            categoria=normativa.categoria,
            estado='vigente'
        ).exclude(id=normativa.id)[:4]
    
    # Inspecciones relacionadas
    inspecciones_recientes = normativa.inspecciones.order_by('-fecha_inspeccion')[:5]
    
    # Incidentes que involucran esta normativa
    incidentes_relacionados = IncidenteSeguridad.objects.filter(
        normativas_incumplidas=normativa
    ).order_by('-fecha_incidente')[:3]
    
    # Historial de cambios
    historial = normativa.historial.order_by('-fecha')[:10]
    
    context = {
        'normativa': normativa,
        'normativas_relacionadas': normativas_relacionadas,
        'inspecciones_recientes': inspecciones_recientes,
        'incidentes_relacionados': incidentes_relacionados,
        'historial': historial,
        'es_admin': es_staff_o_admin(request.user),
    }
    
    return render(request, 'sistema_interno/ver_normativa.html', context)

@login_required
@user_passes_test(es_staff_o_admin)
def crear_normativa_view(request):
    """Vista para crear una nueva normativa"""
    
    if request.method == 'POST':
        form = NormativaSeguridadForm(request.POST, request.FILES)
        if form.is_valid():
            normativa = form.save(commit=False)
            normativa.autor = request.user
            
            # Si se marca como vigente, establecer fecha de aprobación
            if normativa.estado == 'vigente':
                normativa.aprobado_por = request.user
                normativa.fecha_aprobacion = timezone.now()
                normativa.fecha_publicacion = timezone.now()
            
            normativa.save()
            form.save_m2m()  # Guardar relaciones many-to-many
            
            # Registrar en historial
            HistorialNormativa.objects.create(
                normativa=normativa,
                usuario=request.user,
                accion='crear',
                descripcion=f'Normativa creada: {normativa.titulo}',
                version_nueva=normativa.version
            )
            
            messages.success(
                request, 
                f'Normativa "{normativa.titulo}" creada exitosamente.'
            )
            return redirect('normativas:ver-normativa', normativa_id=normativa.id)
        else:
            messages.error(
                request, 
                'Error al crear la normativa. Revise los datos ingresados.'
            )
    else:
        form = NormativaSeguridadForm()
    
    context = {
        'form': form,
        'titulo': 'Crear Nueva Normativa de Seguridad',
        'accion': 'crear',
    }
    
    return render(request, 'sistema_interno/form_normativa.html', context)

@login_required
@user_passes_test(es_staff_o_admin)
def editar_normativa_view(request, normativa_id):
    """Vista para editar una normativa existente"""
    
    normativa = get_object_or_404(NormativaSeguridad, id=normativa_id)
    datos_anteriores = {
        'titulo': normativa.titulo,
        'version': normativa.version,
        'estado': normativa.estado,
    }
    
    if request.method == 'POST':
        form = NormativaSeguridadForm(request.POST, request.FILES, instance=normativa)
        if form.is_valid():
            # Verificar si es cambio de versión
            version_anterior = normativa.version
            normativa_editada = form.save(commit=False)
            
            # Si cambió la versión, actualizar campos relacionados
            if version_anterior != normativa_editada.version:
                normativa_editada.motivo_actualizacion = form.cleaned_data.get('motivo_actualizacion', '')
                # Buscar versión anterior para vincular
                try:
                    version_ant = NormativaSeguridad.objects.filter(
                        titulo=normativa_editada.titulo,
                        version=version_anterior
                    ).first()
                    if version_ant:
                        normativa_editada.version_anterior = version_ant
                except:
                    pass
            
            # Si se aprueba, establecer datos de aprobación
            if (normativa_editada.estado == 'vigente' and 
                datos_anteriores['estado'] != 'vigente'):
                normativa_editada.aprobado_por = request.user
                normativa_editada.fecha_aprobacion = timezone.now()
                if not normativa_editada.fecha_publicacion:
                    normativa_editada.fecha_publicacion = timezone.now()
            
            normativa_editada.save()
            form.save_m2m()  # Guardar relaciones many-to-many
            
            # Registrar en historial
            accion = 'nueva_version' if version_anterior != normativa_editada.version else 'editar'
            HistorialNormativa.objects.create(
                normativa=normativa_editada,
                usuario=request.user,
                accion=accion,
                descripcion=f'Normativa {accion}: {normativa_editada.titulo}',
                version_anterior=version_anterior,
                version_nueva=normativa_editada.version
            )
            
            messages.success(
                request, 
                f'Normativa "{normativa_editada.titulo}" actualizada exitosamente.'
            )
            return redirect('normativas:ver-normativa', normativa_id=normativa_editada.id)
        else:
            messages.error(
                request, 
                'Error al actualizar la normativa. Revise los datos ingresados.'
            )
    else:
        form = NormativaSeguridadForm(instance=normativa)
    
    context = {
        'form': form,
        'normativa': normativa,
        'titulo': f'Editar Normativa: {normativa.titulo}',
        'accion': 'editar',
    }
    
    return render(request, 'sistema_interno/form_normativa.html', context)

@login_required
@user_passes_test(es_staff_o_admin)
def eliminar_normativa_view(request, normativa_id):
    """Vista para eliminar/archivar una normativa"""
    
    normativa = get_object_or_404(NormativaSeguridad, id=normativa_id)
    
    # Verificar si se puede eliminar (no tiene dependencias críticas)
    tiene_incidentes = IncidenteSeguridad.objects.filter(
        normativas_incumplidas=normativa
    ).exists()
    
    tiene_inspecciones = InspeccionSeguridad.objects.filter(
        normativa=normativa
    ).exists()
    
    tiene_capacitaciones = CapacitacionSeguridad.objects.filter(
        normativas_cubiertas=normativa
    ).exists()
    
    puede_eliminar = not (tiene_incidentes or tiene_inspecciones or tiene_capacitaciones)
    
    if request.method == 'POST':
        accion = request.POST.get('accion')
        
        if accion == 'archivar':
            # Archivar la normativa
            estado_anterior = normativa.estado
            normativa.estado = 'archivada'
            normativa.save(update_fields=['estado'])
            
            # Registrar en historial
            HistorialNormativa.objects.create(
                normativa=normativa,
                usuario=request.user,
                accion='archivar',
                descripcion=f'Normativa archivada: {normativa.titulo}',
                datos_antiguos={'estado': estado_anterior},
                datos_nuevos={'estado': 'archivada'}
            )
            
            messages.success(
                request, 
                f'Normativa "{normativa.titulo}" archivada exitosamente.'
            )
            
        elif accion == 'eliminar' and puede_eliminar:
            # Eliminar permanentemente
            titulo = normativa.titulo
            normativa.delete()
            
            messages.success(
                request, 
                f'Normativa "{titulo}" eliminada permanentemente.'
            )
        
        elif accion == 'eliminar' and not puede_eliminar:
            messages.error(
                request, 
                'No se puede eliminar esta normativa porque tiene registros asociados. '
                'Puede archivala en su lugar.'
            )
            return redirect('normativas:eliminar-normativa', normativa_id=normativa.id)
        
        return redirect('normativas:normativas')
    
    context = {
        'normativa': normativa,
        'puede_eliminar': puede_eliminar,
        'tiene_incidentes': tiene_incidentes,
        'tiene_inspecciones': tiene_inspecciones,
        'tiene_capacitaciones': tiene_capacitaciones,
    }
    
    return render(request, 'sistema_interno/eliminar_normativa.html', context)

@login_required
def incidentes_view(request):
    """Vista para gestionar incidentes de seguridad"""
    
    # Filtros
    gravedad_filtro = request.GET.get('gravedad', '')
    tipo_filtro = request.GET.get('tipo', '')
    estado_filtro = request.GET.get('estado', '')
    area_filtro = request.GET.get('area', '')
    busqueda = request.GET.get('busqueda', '')
    
    # Query base
    incidentes = IncidenteSeguridad.objects.select_related(
        'reportado_por', 'investigador_asignado'
    ).order_by('-fecha_incidente')
    
    # Aplicar filtros
    if gravedad_filtro:
        incidentes = incidentes.filter(gravedad=gravedad_filtro)
    
    if tipo_filtro:
        incidentes = incidentes.filter(tipo_incidente=tipo_filtro)
    
    if estado_filtro:
        incidentes = incidentes.filter(estado=estado_filtro)
    
    if area_filtro:
        incidentes = incidentes.filter(area_afectada__icontains=area_filtro)
    
    if busqueda:
        incidentes = incidentes.filter(
            Q(numero_incidente__icontains=busqueda) |
            Q(descripcion_incidente__icontains=busqueda) |
            Q(area_afectada__icontains=busqueda)
        )
    
    # Estadísticas
    stats_incidentes = {
        'total': IncidenteSeguridad.objects.count(),
        'este_mes': IncidenteSeguridad.objects.filter(
            fecha_incidente__gte=timezone.now().replace(day=1)
        ).count(),
        'pendientes': IncidenteSeguridad.objects.filter(
            estado__in=['reportado', 'investigando']
        ).count(),
        'criticos': IncidenteSeguridad.objects.filter(
            gravedad='critico'
        ).count(),
    }
    
    # Paginación
    paginator = Paginator(incidentes, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'incidentes': page_obj,
        'page_obj': page_obj,
        'stats_incidentes': stats_incidentes,
        'es_admin': es_staff_o_admin(request.user),
        'gravedad_filtro': gravedad_filtro,
        'tipo_filtro': tipo_filtro,
        'estado_filtro': estado_filtro,
        'area_filtro': area_filtro,
        'busqueda': busqueda,
        'gravedades': IncidenteSeguridad.GRAVEDAD_CHOICES,
        'tipos': IncidenteSeguridad.TIPO_INCIDENTE_CHOICES,
        'estados': IncidenteSeguridad.ESTADO_CHOICES,
    }
    
    return render(request, 'sistema_interno/incidentes.html', context)

@login_required
@user_passes_test(es_staff_o_admin)
def crear_incidente_view(request):
    """Vista para reportar un nuevo incidente"""
    
    if request.method == 'POST':
        form = IncidenteSeguridadForm(request.POST, request.FILES)
        if form.is_valid():
            incidente = form.save(commit=False)
            incidente.reportado_por = request.user
            incidente.save()
            form.save_m2m()  # Guardar normativas incumplidas
            
            messages.success(
                request, 
                f'Incidente {incidente.numero_incidente} reportado exitosamente.'
            )
            return redirect('normativas:incidentes')
        else:
            messages.error(
                request, 
                'Error al reportar el incidente. Revise los datos ingresados.'
            )
    else:
        form = IncidenteSeguridadForm()
    
    context = {
        'form': form,
        'titulo': 'Reportar Nuevo Incidente de Seguridad',
        'accion': 'crear',
    }
    
    return render(request, 'sistema_interno/form_incidente.html', context)

@login_required
def inspecciones_view(request):
    """Vista para gestionar inspecciones de seguridad"""
    
    # Filtros
    resultado_filtro = request.GET.get('resultado', '')
    tipo_filtro = request.GET.get('tipo', '')
    normativa_filtro = request.GET.get('normativa', '')
    area_filtro = request.GET.get('area', '')
    vencidas = request.GET.get('vencidas', '')
    
    # Query base
    inspecciones = InspeccionSeguridad.objects.select_related(
        'normativa', 'inspector', 'verificado_por'
    ).order_by('-fecha_inspeccion')
    
    # Aplicar filtros
    if resultado_filtro:
        inspecciones = inspecciones.filter(resultado=resultado_filtro)
    
    if tipo_filtro:
        inspecciones = inspecciones.filter(tipo_inspeccion=tipo_filtro)
    
    if normativa_filtro:
        inspecciones = inspecciones.filter(normativa_id=normativa_filtro)
    
    if area_filtro:
        inspecciones = inspecciones.filter(area_inspeccionada__icontains=area_filtro)
    
    if vencidas:
        inspecciones = inspecciones.filter(
            fecha_limite_correccion__lt=timezone.now().date(),
            corregido=False
        )
    
    # Estadísticas
    stats_inspecciones = {
        'total': InspeccionSeguridad.objects.count(),
        'este_mes': InspeccionSeguridad.objects.filter(
            fecha_inspeccion__gte=timezone.now().replace(day=1)
        ).count(),
        'vencidas': InspeccionSeguridad.objects.filter(
            fecha_limite_correccion__lt=timezone.now().date(),
            corregido=False
        ).count(),
        'cumple': InspeccionSeguridad.objects.filter(
            resultado='cumple'
        ).count(),
    }
    
    # Paginación
    paginator = Paginator(inspecciones, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'inspecciones': page_obj,
        'page_obj': page_obj,
        'stats_inspecciones': stats_inspecciones,
        'es_admin': es_staff_o_admin(request.user),
        'resultado_filtro': resultado_filtro,
        'tipo_filtro': tipo_filtro,
        'normativa_filtro': normativa_filtro,
        'area_filtro': area_filtro,
        'vencidas': vencidas,
        'resultados': InspeccionSeguridad.RESULTADO_CHOICES,
        'tipos': InspeccionSeguridad.TIPO_INSPECCION_CHOICES,
        'normativas': NormativaSeguridad.objects.filter(estado='vigente'),
    }
    
    return render(request, 'sistema_interno/inspecciones.html', context)

@login_required
def capacitaciones_view(request):
    """Vista para gestionar capacitaciones de seguridad"""
    
    # Filtros
    estado_filtro = request.GET.get('estado', '')
    modalidad_filtro = request.GET.get('modalidad', '')
    obligatoria_filtro = request.GET.get('obligatoria', '')
    fecha_filtro = request.GET.get('fecha', '')
    
    # Query base
    capacitaciones = CapacitacionSeguridad.objects.select_related(
        'creado_por'
    ).prefetch_related('normativas_cubiertas').order_by('-fecha_inicio')
    
    # Aplicar filtros
    if estado_filtro:
        capacitaciones = capacitaciones.filter(estado=estado_filtro)
    
    if modalidad_filtro:
        capacitaciones = capacitaciones.filter(modalidad=modalidad_filtro)
    
    if obligatoria_filtro:
        capacitaciones = capacitaciones.filter(es_obligatoria=True)
    
    if fecha_filtro == 'proximas':
        capacitaciones = capacitaciones.filter(fecha_inicio__gte=timezone.now())
    elif fecha_filtro == 'pasadas':
        capacitaciones = capacitaciones.filter(fecha_inicio__lt=timezone.now())
    
    # Estadísticas
    stats_capacitaciones = {
        'total': CapacitacionSeguridad.objects.count(),
        'programadas': CapacitacionSeguridad.objects.filter(estado='programada').count(),
        'en_curso': CapacitacionSeguridad.objects.filter(estado='en_curso').count(),
        'completadas': CapacitacionSeguridad.objects.filter(estado='completada').count(),
    }
    
    # Paginación
    paginator = Paginator(capacitaciones, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'capacitaciones': page_obj,
        'page_obj': page_obj,
        'stats_capacitaciones': stats_capacitaciones,
        'es_admin': es_staff_o_admin(request.user),
        'estado_filtro': estado_filtro,
        'modalidad_filtro': modalidad_filtro,
        'obligatoria_filtro': obligatoria_filtro,
        'fecha_filtro': fecha_filtro,
        'estados': CapacitacionSeguridad.ESTADO_CHOICES,
        'modalidades': CapacitacionSeguridad.MODALIDAD_CHOICES,
    }
    
    return render(request, 'sistema_interno/capacitaciones.html', context)

@login_required
@require_POST
def descargar_normativa_view(request, normativa_id):
    """Vista para descargar archivo de normativa"""
    import os
    import mimetypes
    
    normativa = get_object_or_404(NormativaSeguridad, id=normativa_id)
    
    # Incrementar contador de descargas
    normativa.incrementar_descarga(request.user)
    
    if normativa.archivo_principal and os.path.exists(normativa.archivo_principal.path):
        # Determinar tipo de contenido
        content_type, _ = mimetypes.guess_type(normativa.archivo_principal.path)
        if content_type is None:
            content_type = 'application/octet-stream'
        
        # Preparar respuesta de descarga
        with open(normativa.archivo_principal.path, 'rb') as archivo:
            response = HttpResponse(archivo.read(), content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{normativa.archivo_principal.name}"'
            return response
    else:
        messages.error(request, 'El archivo de la normativa no está disponible.')
        return redirect('normativas:ver-normativa', normativa_id=normativa.id)

# APIs para estadísticas
@login_required
def api_normativa_stats(request, normativa_id):
    """API para obtener estadísticas de una normativa"""
    normativa = get_object_or_404(NormativaSeguridad, id=normativa_id)
    
    stats = {
        'vistas': normativa.vistas,
        'descargas': normativa.descargas,
        'fecha_modificacion': normativa.fecha_modificacion.isoformat(),
        'estado': normativa.estado,
        'dias_para_revision': normativa.dias_para_revision,
    }
    
    return JsonResponse({'success': True, 'stats': stats})

@login_required
def api_dashboard_stats(request):
    """API para estadísticas del dashboard"""
    stats = {
        'normativas_vigentes': NormativaSeguridad.objects.filter(estado='vigente').count(),
        'incidentes_pendientes': IncidenteSeguridad.objects.filter(
            estado__in=['reportado', 'investigando']
        ).count(),
        'inspecciones_vencidas': InspeccionSeguridad.objects.filter(
            fecha_limite_correccion__lt=timezone.now().date(),
            corregido=False
        ).count(),
        'capacitaciones_proximas': CapacitacionSeguridad.objects.filter(
            estado='programada',
            fecha_inicio__gte=timezone.now(),
            fecha_inicio__lte=timezone.now() + timezone.timedelta(days=7)
        ).count(),
    }
    
    return JsonResponse({'success': True, 'stats': stats})

# Vista para gestión administrativa
@login_required
@user_passes_test(es_staff_o_admin)
def gestionar_normativas_view(request):
    """Vista administrativa para gestionar todas las normativas"""
    
    # Obtener todas las normativas (incluyendo borradores)
    normativas = NormativaSeguridad.objects.all().select_related(
        'categoria', 'autor', 'aprobado_por'
    ).order_by('-fecha_modificacion')
    
    # Filtros
    estado_filtro = request.GET.get('estado', '')
    categoria_filtro = request.GET.get('categoria', '')
    autor_filtro = request.GET.get('autor', '')
    busqueda = request.GET.get('busqueda', '')
    
    if estado_filtro:
        normativas = normativas.filter(estado=estado_filtro)
    
    if categoria_filtro:
        normativas = normativas.filter(categoria_id=categoria_filtro)
    
    if autor_filtro:
        normativas = normativas.filter(autor_id=autor_filtro)
    
    if busqueda:
        normativas = normativas.filter(
            Q(titulo__icontains=busqueda) |
            Q(codigo__icontains=busqueda) |
            Q(descripcion__icontains=busqueda)
        )
    
    # Paginación
    paginator = Paginator(normativas, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estadísticas para administradores
    stats_admin = {
        'total_normativas': NormativaSeguridad.objects.count(),
        'vigentes': NormativaSeguridad.objects.filter(estado='vigente').count(),
        'borradores': NormativaSeguridad.objects.filter(estado='borrador').count(),
        'en_revision': NormativaSeguridad.objects.filter(estado='revision').count(),
        'obsoletas': NormativaSeguridad.objects.filter(estado='obsoleta').count(),
        'por_vencer': NormativaSeguridad.objects.filter(
            proxima_revision__lte=timezone.now().date() + timezone.timedelta(days=30)
        ).count(),
    }
    
    context = {
        'normativas': page_obj,
        'page_obj': page_obj,
        'stats_admin': stats_admin,
        'estado_filtro': estado_filtro,
        'categoria_filtro': categoria_filtro,
        'autor_filtro': autor_filtro,
        'busqueda': busqueda,
        'categorias': CategoriaSeguridad.objects.filter(activo=True),
        'estados': NormativaSeguridad.ESTADO_CHOICES,
        'autores': User.objects.filter(normativas_creadas__isnull=False).distinct(),
    }
    
    return render(request, 'sistema_interno/gestionar_normativas.html', context)

@login_required
def seguridad_industrial_view(request):
    """Vista principal del módulo de Seguridad Industrial"""
    
    # Estadísticas principales
    stats = {
        'normativas_vigentes': NormativaSeguridad.objects.filter(estado='vigente').count(),
        'incidentes_este_mes': IncidenteSeguridad.objects.filter(
            fecha_incidente__gte=timezone.now().replace(day=1)
        ).count(),
        'inspecciones_pendientes': InspeccionSeguridad.objects.filter(
            fecha_limite_correccion__lt=timezone.now().date(),
            corregido=False
        ).count(),
        'cumplimiento_promedio': 85,  # Calcular basado en inspecciones
        'porcentaje_inspecciones': 78,  # Calcular basado en inspecciones completadas
        'porcentaje_capacitaciones': 92,  # Calcular basado en capacitaciones completadas
    }
    
    # Normativas críticas (máximo 5)
    normativas_criticas = NormativaSeguridad.objects.filter(
        estado='vigente',
        prioridad='critica'
    ).select_related('categoria').order_by('-fecha_modificacion')[:5]
    
    # Incidentes recientes (máximo 6)
    incidentes_recientes = IncidenteSeguridad.objects.select_related(
        'reportado_por'
    ).order_by('-fecha_incidente')[:6]
    
    # Inspecciones recientes (máximo 5)
    inspecciones_recientes = InspeccionSeguridad.objects.select_related(
        'normativa', 'inspector'
    ).order_by('-fecha_inspeccion')[:5]
    
    # Capacitaciones próximas (máximo 4)
    capacitaciones_proximas = CapacitacionSeguridad.objects.filter(
        estado__in=['programada', 'en_curso'],
        fecha_inicio__gte=timezone.now()
    ).order_by('fecha_inicio')[:4]
    
    # Alerta crítica (si existe)
    alerta_critica = None
    
    # Verificar si hay incidentes críticos sin resolver
    incidentes_criticos = IncidenteSeguridad.objects.filter(
        gravedad='critico',
        estado__in=['reportado', 'investigando']
    ).count()
    
    if incidentes_criticos > 0:
        alerta_critica = {
            'titulo': 'Incidentes Críticos Pendientes',
            'mensaje': f'Hay {incidentes_criticos} incidente(s) crítico(s) que requieren atención inmediata.'
        }
    
    # Verificar normativas por vencer
    normativas_vencen = NormativaSeguridad.objects.filter(
        estado='vigente',
        proxima_revision__lte=timezone.now().date() + timezone.timedelta(days=7)
    ).count()
    
    if normativas_vencen > 0 and not alerta_critica:
        alerta_critica = {
            'titulo': 'Normativas Requieren Revisión',
            'mensaje': f'{normativas_vencen} normativa(s) requiere(n) revisión en los próximos 7 días.'
        }
    
    context = {
        'stats': stats,
        'normativas_criticas': normativas_criticas,
        'incidentes_recientes': incidentes_recientes,
        'inspecciones_recientes': inspecciones_recientes,
        'capacitaciones_proximas': capacitaciones_proximas,
        'alerta_critica': alerta_critica,
        'es_admin': es_staff_o_admin(request.user),
    }
    
    return render(request, 'sistema_interno/seguridad_industrial.html', context)

@login_required
def alertas_riesgos_view(request):
    """Vista principal del módulo de Alertas y Gestión de Riesgos"""
    
    # Filtros de la URL
    prioridad_filtro = request.GET.get('prioridad', '')
    area_filtro = request.GET.get('area', '')
    estado_filtro = request.GET.get('estado', '')
    tipo_filtro = request.GET.get('tipo', '')
    
    # Estadísticas principales
    stats = {
        'alertas_criticas': IncidenteSeguridad.objects.filter(
            gravedad='critico',
            estado__in=['reportado', 'investigando']
        ).count(),
        'riesgos_altos': 5,  # Placeholder - implementar modelo de evaluación de riesgos
        'incidentes_hoy': IncidenteSeguridad.objects.filter(
            fecha_incidente__date=timezone.now().date()
        ).count(),
        'normativas_vencidas': NormativaSeguridad.objects.filter(
            proxima_revision__lt=timezone.now().date(),
            estado='vigente'
        ).count(),
        'nivel_riesgo_general': 72,  # Placeholder - calcular basado en evaluaciones
    }
    
    # Simular alertas activas (basadas en incidentes y normativas)
    alertas_activas = []
    
    # Incidentes críticos como alertas
    incidentes_criticos = IncidenteSeguridad.objects.filter(
        estado__in=['reportado', 'investigando']
    ).order_by('-fecha_incidente')[:10]
    
    for incidente in incidentes_criticos:
        alertas_activas.append({
            'id': f'inc_{incidente.id}',
            'titulo': f'Incidente {incidente.get_tipo_incidente_display()}',
            'descripcion': incidente.descripcion_incidente,
            'prioridad': incidente.gravedad,
            'area_afectada': incidente.area_afectada,
            'tipo': 'seguridad',
            'estado': incidente.estado,
            'fecha_creacion': incidente.fecha_incidente,
        })
    
    # Normativas vencidas como alertas
    normativas_vencidas = NormativaSeguridad.objects.filter(
        proxima_revision__lt=timezone.now().date(),
        estado='vigente'
    ).order_by('proxima_revision')[:5]
    
    for normativa in normativas_vencidas:
        dias_vencida = (timezone.now().date() - normativa.proxima_revision).days
        prioridad = 'critica' if dias_vencida > 30 else 'alta' if dias_vencida > 7 else 'media'
        
        alertas_activas.append({
            'id': f'norm_{normativa.id}',
            'titulo': f'Normativa Vencida: {normativa.titulo}',
            'descripcion': f'Requiere revisión desde hace {dias_vencida} días',
            'prioridad': prioridad,
            'area_afectada': normativa.get_ambito_aplicacion_display(),
            'tipo': 'normativa',
            'estado': 'pendiente',
            'fecha_creacion': normativa.proxima_revision,
        })
    
    # Inspecciones vencidas como alertas
    inspecciones_vencidas = InspeccionSeguridad.objects.filter(
        fecha_limite_correccion__lt=timezone.now().date(),
        corregido=False
    ).order_by('fecha_limite_correccion')[:5]
    
    for inspeccion in inspecciones_vencidas:
        dias_vencida = (timezone.now().date() - inspeccion.fecha_limite_correccion).days
        prioridad = 'critica' if dias_vencida > 15 else 'alta' if dias_vencida > 3 else 'media'
        
        alertas_activas.append({
            'id': f'insp_{inspeccion.id}',
            'titulo': f'Corrección Vencida: {inspeccion.normativa.titulo}',
            'descripcion': f'Observaciones sin corregir desde hace {dias_vencida} días',
            'prioridad': prioridad,
            'area_afectada': inspeccion.area_inspeccionada,
            'tipo': 'mantenimiento',
            'estado': 'pendiente',
            'fecha_creacion': inspeccion.fecha_limite_correccion,
        })
    
    # Convertir a objetos simulados para compatibilidad con template
    class AlertaSimulada:
        def __init__(self, data):
            for key, value in data.items():
                setattr(self, key, value)
        
        def get_estado_display(self):
            estados = {
                'pendiente': 'Pendiente',
                'en-progreso': 'En Progreso',
                'resuelto': 'Resuelto',
                'reportado': 'Reportado',
                'investigando': 'Investigando'
            }
            return estados.get(self.estado, self.estado.title())
        
        def get_prioridad_display(self):
            prioridades = {
                'critica': 'Crítica',
                'alta': 'Alta',
                'media': 'Media',
                'baja': 'Baja'
            }
            return prioridades.get(self.prioridad, self.prioridad.title())
    
    # Aplicar filtros
    alertas_filtradas = alertas_activas
    
    if prioridad_filtro:
        alertas_filtradas = [a for a in alertas_filtradas if a['prioridad'] == prioridad_filtro]
    
    if area_filtro:
        alertas_filtradas = [a for a in alertas_filtradas if area_filtro.lower() in a['area_afectada'].lower()]
    
    if estado_filtro:
        alertas_filtradas = [a for a in alertas_filtradas if a['estado'] == estado_filtro]
    
    if tipo_filtro:
        alertas_filtradas = [a for a in alertas_filtradas if a['tipo'] == tipo_filtro]
    
    # Convertir a objetos simulados
    alertas_activas_obj = [AlertaSimulada(alerta) for alerta in alertas_filtradas[:15]]
    
    # Alerta crítica activa (la más importante)
    alerta_critica_activa = None
    if stats['alertas_criticas'] > 0:
        incidente_critico = IncidenteSeguridad.objects.filter(
            gravedad='critico',
            estado__in=['reportado', 'investigando']
        ).order_by('-fecha_incidente').first()
        
        if incidente_critico:
            alerta_critica_activa = {
                'titulo': 'Incidente Crítico Activo',
                'descripcion': f'Se ha reportado un incidente crítico en {incidente_critico.area_afectada}. '
                              f'Se requiere atención inmediata para resolver la situación.'
            }
    
    # Riesgos identificados (simulados)
    riesgos_identificados = [
        {
            'descripcion_riesgo': 'Exposición a altas temperaturas en área de soldadura',
            'area_evaluada': 'Taller de Soldadura',
            'probabilidad': 4,
            'impacto': 4,
            'nivel_riesgo': 'alto'
        },
        {
            'descripcion_riesgo': 'Riesgo de cortes en máquinas de maquinado',
            'area_evaluada': 'Taller de Maquinado',
            'probabilidad': 3,
            'impacto': 3,
            'nivel_riesgo': 'medio'
        },
        {
            'descripcion_riesgo': 'Inhalación de vapores metálicos en fundición',
            'area_evaluada': 'Área de Fundición',
            'probabilidad': 2,
            'impacto': 4,
            'nivel_riesgo': 'medio'
        }
    ]
    
    # Convertir riesgos a objetos simulados
    class RiesgoSimulado:
        def __init__(self, data):
            for key, value in data.items():
                setattr(self, key, value)
        
        def get_nivel_riesgo_display(self):
            niveles = {
                'muy_bajo': 'Muy Bajo',
                'bajo': 'Bajo',
                'medio': 'Medio',
                'alto': 'Alto',
                'critico': 'Crítico'
            }
            return niveles.get(self.nivel_riesgo, self.nivel_riesgo.title())
    
    riesgos_identificados_obj = [RiesgoSimulado(riesgo) for riesgo in riesgos_identificados]
    
    # Estadísticas por área
    estadisticas_areas = [
        {
            'nombre': 'Soldadura',
            'total_alertas': 3,
            'alertas_criticas': 1,
            'alertas_altas': 2
        },
        {
            'nombre': 'Maquinado',
            'total_alertas': 2,
            'alertas_criticas': 0,
            'alertas_altas': 1
        },
        {
            'nombre': 'Fundición',
            'total_alertas': 1,
            'alertas_criticas': 0,
            'alertas_altas': 0
        },
        {
            'nombre': 'Almacén',
            'total_alertas': 1,
            'alertas_criticas': 0,
            'alertas_altas': 1
        }
    ]
    
    # Últimas acciones (historial simulado)
    ultimas_acciones = []
    
    # Agregar historial de normativas reciente
    historial_reciente = HistorialNormativa.objects.order_by('-fecha')[:5]
    for historial in historial_reciente:
        ultimas_acciones.append({
            'descripcion': f'{historial.get_accion_display()}: {historial.normativa.titulo}',
            'fecha': historial.fecha,
            'usuario': historial.usuario,
            'tipo': 'normativa',
        })
    
    context = {
        'stats': stats,
        'alertas_activas': alertas_activas_obj,
        'alerta_critica_activa': alerta_critica_activa,
        'riesgos_identificados': riesgos_identificados_obj,
        'estadisticas_areas': estadisticas_areas,
        'ultimas_acciones': ultimas_acciones,
        'es_admin': es_staff_o_admin(request.user),
        'prioridad_filtro': prioridad_filtro,
        'area_filtro': area_filtro,
        'estado_filtro': estado_filtro,
        'tipo_filtro': tipo_filtro,
    }
    
    return render(request, 'sistema_interno/alertas_riesgos.html', context)
