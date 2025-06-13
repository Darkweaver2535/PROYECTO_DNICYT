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
            'titulo': 'Normativas requieren revisión',
            'mensaje': f'{stats["por_revisar"]} normativas necesitan revisión en los próximos 30 días',
            'icono': 'bi-exclamation-triangle',
            'url': '?estado=vigente&por_revisar=1'
        })
    
    # Alertas de incidentes sin resolver
    incidentes_pendientes = IncidenteSeguridad.objects.filter(
        estado__in=['reportado', 'investigando']
    ).count()
    
    if incidentes_pendientes > 0:
        alertas.append({
            'tipo': 'danger',
            'titulo': 'Incidentes pendientes',
            'mensaje': f'{incidentes_pendientes} incidentes requieren atención',
            'icono': 'bi-exclamation-circle',
            'url': reverse('normativas:incidentes')
        })
    
    # Alertas de inspecciones vencidas
    inspecciones_vencidas = InspeccionSeguridad.objects.filter(
        fecha_limite_correccion__lt=timezone.now().date(),
        corregido=False
    ).count()
    
    if inspecciones_vencidas > 0:
        alertas.append({
            'tipo': 'warning',
            'titulo': 'Acciones correctivas vencidas',
            'mensaje': f'{inspecciones_vencidas} inspecciones tienen acciones correctivas vencidas',
            'icono': 'bi-clock',
            'url': reverse('normativas:inspecciones')
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
        # Filtros actuales
        'categoria_filtro': categoria_filtro,
        'tipo_filtro': tipo_filtro,
        'prioridad_filtro': prioridad_filtro,
        'ambito_filtro': ambito_filtro,
        'estado_filtro': estado_filtro,
        'busqueda': busqueda,
        # Opciones para filtros
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
            normativa.save()
            form.save_m2m()  # Guardar relaciones many-to-many
            
            # Registrar en historial
            HistorialNormativa.objects.create(
                normativa=normativa,
                usuario=request.user,
                accion='crear',
                descripcion=f'Normativa creada: {normativa.titulo}',
            )
            
            messages.success(request, f'Normativa "{normativa.titulo}" creada exitosamente.')
            return redirect('normativas:ver-normativa', normativa_id=normativa.id)
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
    
    if request.method == 'POST':
        form = NormativaSeguridadForm(request.POST, request.FILES, instance=normativa)
        if form.is_valid():
            # Registrar cambio en historial
            HistorialNormativa.objects.create(
                normativa=normativa,
                usuario=request.user,
                accion='editar',
                descripcion=f'Normativa editada: {normativa.titulo}',
            )
            
            form.save()
            
            messages.success(request, f'Normativa "{normativa.titulo}" actualizada exitosamente.')
            return redirect('normativas:ver-normativa', normativa_id=normativa.id)
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
            form.save_m2m()
            
            messages.success(request, f'Incidente {incidente.numero_incidente} reportado exitosamente.')
            return redirect('normativas:ver-incidente', incidente_id=incidente.id)
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
    
    normativa = get_object_or_404(NormativaSeguridad, id=normativa_id)
    
    # Incrementar contador de descargas
    normativa.incrementar_descarga(request.user)
    
    if normativa.archivo_principal and os.path.exists(normativa.archivo_principal.path):
        try:
            archivo_path = normativa.archivo_principal.path
            content_type, _ = mimetypes.guess_type(archivo_path)
            if not content_type:
                content_type = 'application/octet-stream'
            
            with open(archivo_path, 'rb') as archivo:
                response = HttpResponse(archivo.read(), content_type=content_type)
                filename = f"{normativa.codigo}_{normativa.titulo}_v{normativa.version}.pdf"
                filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                response['Content-Length'] = os.path.getsize(archivo_path)
                return response
                
        except Exception as e:
            messages.error(request, f'Error al descargar el archivo: {str(e)}')
            return redirect('normativas:ver-normativa', normativa_id=normativa.id)
    
    # Si no hay archivo, generar PDF de demostración
    else:
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            from io import BytesIO
            
            buffer = BytesIO()
            p = canvas.Canvas(buffer, pagesize=letter)
            width, height = letter
            
            # Encabezado
            p.setFont("Helvetica-Bold", 18)
            p.drawString(50, height - 50, f"NORMATIVA DE SEGURIDAD")
            
            # Información de la normativa
            p.setFont("Helvetica-Bold", 14)
            y_position = height - 100
            p.drawString(50, y_position, f"Código: {normativa.codigo}")
            
            y_position -= 30
            p.setFont("Helvetica-Bold", 16)
            p.drawString(50, y_position, f"Título: {normativa.titulo}")
            
            # Información detallada
            p.setFont("Helvetica", 12)
            y_position -= 40
            info_lines = [
                f"Tipo: {normativa.get_tipo_display()}",
                f"Categoría: {normativa.categoria.nombre}",
                f"Prioridad: {normativa.get_prioridad_display()}",
                f"Ámbito: {normativa.get_ambito_aplicacion_display()}",
                f"Estado: {normativa.get_estado_display()}",
                f"Versión: {normativa.version}",
                f"Fecha de vigencia: {normativa.fecha_vigencia_inicio.strftime('%d/%m/%Y')}",
                f"Autor: {normativa.autor.get_full_name() if normativa.autor else 'No especificado'}",
            ]
            
            for line in info_lines:
                p.drawString(50, y_position, line)
                y_position -= 20
            
            # Descripción
            y_position -= 20
            p.setFont("Helvetica-Bold", 14)
            p.drawString(50, y_position, "DESCRIPCIÓN:")
            
            y_position -= 25
            p.setFont("Helvetica", 11)
            
            # Procesar descripción en líneas
            descripcion = normativa.descripcion or "Sin descripción disponible."
            words = descripcion.split()
            lines = []
            current_line = ""
            
            for word in words:
                if len(current_line + " " + word) < 80:
                    current_line += " " + word if current_line else word
                else:
                    lines.append(current_line)
                    current_line = word
            
            if current_line:
                lines.append(current_line)
            
            for line in lines[:15]:  # Máximo 15 líneas
                p.drawString(50, y_position, line)
                y_position -= 15
                if y_position < 150:
                    break
            
            # Objetivos si existen
            if normativa.objetivos and y_position > 150:
                y_position -= 30
                p.setFont("Helvetica-Bold", 14)
                p.drawString(50, y_position, "OBJETIVOS:")
                
                y_position -= 25
                p.setFont("Helvetica", 11)
                
                objetivos = normativa.objetivos_lista
                for objetivo in objetivos[:5]:
                    if y_position > 100:
                        p.drawString(50, y_position, f"• {objetivo}")
                        y_position -= 15
            
            # Pie de página
            p.setFont("Helvetica-Italic", 10)
            p.drawString(50, 50, f"Sistema de Normativas y Seguridad - Lab Metal Mecá
