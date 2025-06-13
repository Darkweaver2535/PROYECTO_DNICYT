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
import re

from .models import CursoTaller, CategoriaCapacitacion, InscripcionCurso, HistorialVisualizacion, DocumentoTecnico, ValoracionDocumento, HistorialDocumento
from .forms import CursoTallerForm, CategoriaCapacitacionForm, FiltrosCursosForm, InscripcionCursoForm, DocumentoTecnicoForm, FiltrosDocumentosForm, ValoracionDocumentoForm

def es_staff_o_admin(user):
    """Verifica si el usuario es staff o admin"""
    return user.is_authenticated and (user.is_staff or user.is_superuser)

@login_required
def biblioteca_cursos_view(request):
    """Vista principal de la biblioteca de cursos y talleres"""
    
    # Formulario de filtros
    form_filtros = FiltrosCursosForm(request.GET)
    
    # Query base
    cursos = CursoTaller.objects.filter(estado='publicado').select_related('categoria', 'autor')
    
    # Aplicar filtros
    if form_filtros.is_valid():
        data = form_filtros.cleaned_data
        
        if data.get('busqueda'):
            cursos = cursos.filter(
                Q(titulo__icontains=data['busqueda']) |
                Q(descripcion__icontains=data['busqueda']) |
                Q(instructor__icontains=data['busqueda'])
            )
        
        if data.get('categoria'):
            cursos = cursos.filter(categoria=data['categoria'])
        
        if data.get('tipo'):
            cursos = cursos.filter(tipo=data['tipo'])
        
        if data.get('dificultad'):
            cursos = cursos.filter(dificultad=data['dificultad'])
        
        if data.get('modalidad'):
            cursos = cursos.filter(modalidad=data['modalidad'])
        
        if data.get('solo_destacados'):
            cursos = cursos.filter(destacado=True)
        
        if data.get('ordenar'):
            cursos = cursos.order_by(data['ordenar'])
    
    # Estadísticas
    stats = {
        'total_cursos': cursos.count(),
        'categorias_count': CategoriaCapacitacion.objects.filter(activo=True).count(),
        'cursos_destacados': cursos.filter(destacado=True).count(),
        'total_horas': cursos.aggregate(
            total=Sum('duracion_horas')
        )['total'] or 0,
    }
    
    # Mis inscripciones
    mis_inscripciones = InscripcionCurso.objects.filter(
        usuario=request.user
    ).values_list('curso_id', flat=True)
    
    # Paginación
    paginator = Paginator(cursos, 12)  # 12 cursos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Cursos destacados para el sidebar
    cursos_destacados = CursoTaller.objects.filter(
        estado='publicado', 
        destacado=True
    )[:5]
    
    # Categorías para el sidebar
    categorias_stats = CategoriaCapacitacion.objects.filter(
        activo=True
    ).annotate(
        total_cursos=Count('cursos', filter=Q(cursos__estado='publicado'))
    ).order_by('orden')
    
    context = {
        'page_obj': page_obj,
        'form_filtros': form_filtros,
        'stats': stats,
        'mis_inscripciones': mis_inscripciones,
        'cursos_destacados': cursos_destacados,
        'categorias_stats': categorias_stats,
        'es_admin': es_staff_o_admin(request.user),
    }
    
    return render(request, 'sistema_interno/cursos_talleres.html', context)

@login_required
def detalle_curso_view(request, curso_id):
    """Vista detallada de un curso"""
    curso = get_object_or_404(CursoTaller, id=curso_id, estado='publicado')
    
    # Incrementar contador de vistas
    curso.vistas += 1
    curso.save(update_fields=['vistas'])
    
    # Registrar visualización
    HistorialVisualizacion.objects.create(
        curso=curso,
        usuario=request.user
    )
    
    # Verificar si está inscrito
    inscripcion = InscripcionCurso.objects.filter(
        curso=curso,
        usuario=request.user
    ).first()
    
    # Cursos relacionados
    cursos_relacionados = CursoTaller.objects.filter(
        categoria=curso.categoria,
        estado='publicado'
    ).exclude(id=curso.id)[:4]
    
    # Estadísticas del curso
    stats_curso = {
        'total_inscritos': curso.inscripciones.count(),
        'promedio_calificacion': curso.inscripciones.aggregate(
            promedio=Avg('calificacion')
        )['promedio'] or 0,
        'completados': curso.inscripciones.filter(estado='completado').count(),
    }
    
    context = {
        'curso': curso,
        'inscripcion': inscripcion,
        'cursos_relacionados': cursos_relacionados,
        'stats_curso': stats_curso,
        'es_admin': es_staff_o_admin(request.user),
    }
    
    return render(request, 'sistema_interno/detalle_curso_talleres.html', context)

@login_required
@user_passes_test(es_staff_o_admin)
def crear_curso_view(request):
    """Vista para crear un nuevo curso"""
    if request.method == 'POST':
        form = CursoTallerForm(request.POST)
        if form.is_valid():
            curso = form.save(commit=False)
            curso.autor = request.user
            curso.save()
            
            messages.success(request, f'Curso "{curso.titulo}" creado exitosamente.')
            return redirect('capacitacion:detalle-curso', curso_id=curso.id)
    else:
        form = CursoTallerForm()
    
    context = {
        'form': form,
        'titulo': 'Crear Nuevo Curso/Taller',
        'accion': 'crear',
    }
    
    return render(request, 'sistema_interno/form_curso.html', context)

@login_required
@user_passes_test(es_staff_o_admin)
def editar_curso_view(request, curso_id):
    """Vista para editar un curso existente"""
    curso = get_object_or_404(CursoTaller, id=curso_id)
    
    if request.method == 'POST':
        form = CursoTallerForm(request.POST, instance=curso)
        if form.is_valid():
            form.save()
            
            messages.success(request, f'Curso "{curso.titulo}" actualizado exitosamente.')
            return redirect('capacitacion:detalle-curso', curso_id=curso.id)
    else:
        form = CursoTallerForm(instance=curso)
    
    context = {
        'form': form,
        'curso': curso,
        'titulo': f'Editar {curso.get_tipo_display()}',
        'accion': 'editar',
    }
    
    return render(request, 'sistema_interno/form_curso.html', context)

@login_required
@user_passes_test(es_staff_o_admin)
def eliminar_curso_view(request, curso_id):
    """Vista para eliminar un curso"""
    curso = get_object_or_404(CursoTaller, id=curso_id)
    
    if request.method == 'POST':
        titulo = curso.titulo
        curso.delete()
        
        messages.success(request, f'Curso "{titulo}" eliminado exitosamente.')
        return redirect('capacitacion:biblioteca-cursos')
    
    context = {
        'curso': curso,
    }
    
    return render(request, 'sistema_interno/confirmar_eliminar_curso.html', context)

@login_required
@require_POST
def inscribirse_curso_view(request, curso_id):
    """Vista para inscribirse a un curso"""
    curso = get_object_or_404(CursoTaller, id=curso_id, estado='publicado')
    
    # Verificar si ya está inscrito
    inscripcion_existente = InscripcionCurso.objects.filter(
        curso=curso,
        usuario=request.user
    ).first()
    
    if inscripcion_existente:
        messages.warning(request, 'Ya estás inscrito en este curso.')
    else:
        # Verificar límite de participantes
        if curso.max_participantes > 0:
            inscritos_actuales = curso.inscripciones.count()
            if inscritos_actuales >= curso.max_participantes:
                messages.error(request, 'Este curso ha alcanzado el límite de participantes.')
                return redirect('capacitacion:detalle-curso', curso_id=curso.id)
        
        # Crear inscripción
        inscripcion = InscripcionCurso.objects.create(
            curso=curso,
            usuario=request.user,
            comentario=request.POST.get('comentario', '')
        )
        
        messages.success(request, f'Te has inscrito exitosamente en "{curso.titulo}".')
    
    return redirect('capacitacion:detalle-curso', curso_id=curso.id)

@login_required
def mis_cursos_view(request):
    """Vista de cursos del usuario"""
    inscripciones = InscripcionCurso.objects.filter(
        usuario=request.user
    ).select_related('curso', 'curso__categoria').order_by('-fecha_inscripcion')
    
    # Estadísticas del usuario
    stats_usuario = {
        'total_inscritos': inscripciones.count(),
        'completados': inscripciones.filter(estado='completado').count(),
        'en_progreso': inscripciones.filter(estado='en_progreso').count(),
        'horas_totales': sum([
            i.curso.duracion_total_minutos for i in inscripciones if i.estado == 'completado'
        ]) // 60,
    }
    
    context = {
        'inscripciones': inscripciones,
        'stats_usuario': stats_usuario,
    }
    
    return render(request, 'sistema_interno/mis_cursos.html', context)

@login_required
@user_passes_test(es_staff_o_admin)
def gestionar_categorias_view(request):
    """Vista para gestionar categorías"""
    categorias = CategoriaCapacitacion.objects.all().annotate(
        total_cursos=Count('cursos')
    ).order_by('orden')
    
    if request.method == 'POST':
        form = CategoriaCapacitacionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría creada exitosamente.')
            return redirect('capacitacion:gestionar-categorias')
    else:
        form = CategoriaCapacitacionForm()
    
    context = {
        'categorias': categorias,
        'form': form,
    }
    
    return render(request, 'sistema_interno/gestionar_categorias.html', context)

# API Views
@login_required
def api_curso_stats(request, curso_id):
    """API para obtener estadísticas de un curso"""
    curso = get_object_or_404(CursoTaller, id=curso_id)
    
    stats = {
        'vistas': curso.vistas,
        'inscritos': curso.inscripciones.count(),
        'completados': curso.inscripciones.filter(estado='completado').count(),
        'calificacion_promedio': curso.inscripciones.aggregate(
            promedio=Avg('calificacion')
        )['promedio'] or 0,
    }
    
    return JsonResponse({'success': True, 'stats': stats})

# Vista legacy (mantener compatibilidad)
def cursos_talleres_view(request):
    """Redirigir a la nueva vista de biblioteca"""
    return redirect('capacitacion:biblioteca-cursos')

@login_required
def videos_multimedia_view(request):
    """Vista para videos y multimedia - orientada a operarios"""
    
    # Obtener solo cursos con videos (que tengan enlace de YouTube)
    videos_disponibles = CursoTaller.objects.filter(
        estado='publicado',
        enlace_youtube__isnull=False
    ).exclude(enlace_youtube='').select_related('categoria', 'autor').order_by('-fecha_creacion')
    
    # Filtros
    categoria_filtro = request.GET.get('categoria', '')
    tipo_filtro = request.GET.get('tipo', '')
    dificultad_filtro = request.GET.get('dificultad', '')
    busqueda = request.GET.get('busqueda', '')
    
    # Aplicar filtros
    if categoria_filtro:
        videos_disponibles = videos_disponibles.filter(categoria_id=categoria_filtro)
    
    if tipo_filtro:
        videos_disponibles = videos_disponibles.filter(tipo=tipo_filtro)
    
    if dificultad_filtro:
        videos_disponibles = videos_disponibles.filter(dificultad=dificultad_filtro)
    
    if busqueda:
        videos_disponibles = videos_disponibles.filter(
            Q(titulo__icontains=busqueda) |
            Q(descripcion__icontains=busqueda) |
            Q(instructor__icontains=busqueda)
        )
    
    # Videos más vistos
    videos_populares = CursoTaller.objects.filter(
        estado='publicado',
        enlace_youtube__isnull=False
    ).exclude(enlace_youtube='').order_by('-vistas')[:6]
    
    # Videos por categoría para el sidebar
    categorias_stats = CategoriaCapacitacion.objects.filter(
        activo=True,
        cursos__estado='publicado',
        cursos__enlace_youtube__isnull=False
    ).exclude(cursos__enlace_youtube='').annotate(
        total_videos=Count('cursos', filter=Q(cursos__estado='publicado', cursos__enlace_youtube__isnull=False))
    ).order_by('orden')
    
    # Mis videos vistos recientemente
    videos_recientes = HistorialVisualizacion.objects.filter(
        usuario=request.user,
        curso__estado='publicado',
        curso__enlace_youtube__isnull=False
    ).exclude(curso__enlace_youtube='').select_related('curso').order_by('-fecha_visualizacion')[:5]
    
    # Estadísticas
    stats = {
        'total_videos': videos_disponibles.count(),
        'videos_este_mes': videos_disponibles.filter(
            fecha_creacion__gte=timezone.now().replace(day=1)
        ).count(),
        'mis_videos_vistos': HistorialVisualizacion.objects.filter(usuario=request.user).count(),
        'tiempo_total_contenido': sum([v.duracion_total_minutos for v in videos_disponibles]) // 60,
    }
    
    # Paginación
    paginator = Paginator(videos_disponibles, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'videos': page_obj,
        'page_obj': page_obj,
        'videos_populares': videos_populares,
        'videos_recientes': videos_recientes,
        'categorias_stats': categorias_stats,
        'stats': stats,
        'categoria_filtro': categoria_filtro,
        'tipo_filtro': tipo_filtro,
        'dificultad_filtro': dificultad_filtro,
        'busqueda': busqueda,
        'categorias': CategoriaCapacitacion.objects.filter(activo=True),
        'tipos': CursoTaller.TIPO_CHOICES,
        'dificultades': CursoTaller.DIFICULTAD_CHOICES,
    }
    
    return render(request, 'sistema_interno/videos_multimedia.html', context)

@login_required
def reproducir_video_view(request, video_id):
    """Vista para reproducir un video específico"""
    
    video = get_object_or_404(CursoTaller, id=video_id, estado='publicado')
    
    # Incrementar contador de vistas
    video.vistas += 1
    video.save(update_fields=['vistas'])
    
    # Registrar visualización
    HistorialVisualizacion.objects.create(
        curso=video,
        usuario=request.user
    )
    
    # Videos relacionados
    videos_relacionados = CursoTaller.objects.filter(
        categoria=video.categoria,
        estado='publicado',
        enlace_youtube__isnull=False
    ).exclude(id=video.id, enlace_youtube='')[:4]
    
    context = {
        'video': video,
        'videos_relacionados': videos_relacionados,
    }
    
    return render(request, 'sistema_interno/reproducir_video.html', context)

@login_required
def documentos_tecnicos_view(request):
    """Vista principal para documentos técnicos"""
    
    # Filtros del GET
    categoria_filtro = request.GET.get('categoria', '')
    tipo_filtro = request.GET.get('tipo', '')
    formato_filtro = request.GET.get('formato', '')
    dificultad_filtro = request.GET.get('dificultad', '')
    busqueda = request.GET.get('busqueda', '')
    
    # Query base - usar el modelo DocumentoTecnico
    documentos = DocumentoTecnico.objects.filter(
        estado='publicado'
    ).select_related('categoria', 'autor_sistema').order_by('-fecha_modificacion')
    
    # Aplicar filtros
    if categoria_filtro:
        documentos = documentos.filter(categoria_id=categoria_filtro)
    
    if tipo_filtro:
        documentos = documentos.filter(tipo=tipo_filtro)
    
    if formato_filtro:
        documentos = documentos.filter(formato=formato_filtro)
    
    if dificultad_filtro:
        documentos = documentos.filter(dificultad=dificultad_filtro)
    
    if busqueda:
        documentos = documentos.filter(
            Q(titulo__icontains=busqueda) |
            Q(descripcion__icontains=busqueda) |
            Q(autor_documento__icontains=busqueda) |
            Q(palabras_clave__icontains=busqueda)
        )
    
    # Estadísticas
    stats = {
        'total_documentos': documentos.count(),
        'documentos_este_mes': documentos.filter(
            fecha_creacion__gte=timezone.now().replace(day=1)
        ).count(),
        'mis_documentos_vistos': HistorialDocumento.objects.filter(
            usuario=request.user, 
            accion='ver'
        ).count(),
        'categorias_activas': CategoriaCapacitacion.objects.filter(activo=True).count(),
    }
    
    # Documentos más vistos/descargados
    documentos_populares = DocumentoTecnico.objects.filter(
        estado='publicado'
    ).order_by('-vistas', '-descargas')[:6]
    
    # Categorías para el sidebar
    categorias_stats = CategoriaCapacitacion.objects.filter(
        activo=True
    ).annotate(
        total_documentos=Count('documentos_tecnicos', filter=Q(documentos_tecnicos__estado='publicado'))
    ).order_by('orden')
    
    # Documentos vistos recientemente por el usuario
    documentos_recientes = HistorialDocumento.objects.filter(
        usuario=request.user,
        accion='ver'
    ).select_related('documento').order_by('-fecha')[:5]
    
    # Tipos de documentos para sidebar
    tipos_documentos = dict(DocumentoTecnico.TIPO_CHOICES)
    
    # Paginación
    paginator = Paginator(documentos, 15)  # 15 documentos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'documentos': page_obj,
        'page_obj': page_obj,
        'documentos_populares': documentos_populares,
        'documentos_recientes': documentos_recientes,
        'categorias_stats': categorias_stats,
        'stats': stats,
        'tipos_documentos': tipos_documentos,
        'es_admin': es_staff_o_admin(request.user),
        'categoria_filtro': categoria_filtro,
        'tipo_filtro': tipo_filtro,
        'formato_filtro': formato_filtro,
        'dificultad_filtro': dificultad_filtro,
        'busqueda': busqueda,
        'categorias': CategoriaCapacitacion.objects.filter(activo=True),
        'tipos': DocumentoTecnico.TIPO_CHOICES,
        'dificultades': DocumentoTecnico.DIFICULTAD_CHOICES,
    }
    
    return render(request, 'sistema_interno/doc_tecnicos.html', context)

@login_required
def ver_documento_view(request, documento_id):
    """Vista para ver un documento técnico específico"""
    
    documento = get_object_or_404(DocumentoTecnico, id=documento_id, estado='publicado')
    
    # Verificar permisos de confidencialidad
    if not documento.puede_descargar(request.user):
        messages.error(request, 'No tienes permisos para acceder a este documento.')
        return redirect('capacitacion:documentos-tecnicos')
    
    # Incrementar contador de vistas y registrar
    documento.incrementar_vista(request.user)
    
    # Documentos relacionados
    documentos_relacionados = documento.documentos_relacionados.filter(
        estado='publicado'
    )[:4]
    
    # Si no hay relacionados manuales, buscar por categoría
    if not documentos_relacionados.exists():
        documentos_relacionados = DocumentoTecnico.objects.filter(
            categoria=documento.categoria,
            estado='publicado'
        ).exclude(id=documento.id)[:4]
    
    # Valoración del usuario actual
    valoracion_usuario = ValoracionDocumento.objects.filter(
        documento=documento,
        usuario=request.user
    ).first()
    
    # Estadísticas del documento
    stats_documento = {
        'total_vistas': documento.vistas,
        'total_descargas': documento.descargas,
        'valoracion_promedio': documento.valoracion_promedio,
        'total_valoraciones': documento.valoraciones.count(),
    }
    
    context = {
        'documento': documento,
        'documentos_relacionados': documentos_relacionados,
        'valoracion_usuario': valoracion_usuario,
        'stats_documento': stats_documento,
        'es_admin': es_staff_o_admin(request.user),
    }
    
    return render(request, 'sistema_interno/ver_documento.html', context)

@login_required
@user_passes_test(es_staff_o_admin)
def crear_documento_view(request):
    """Vista para crear un nuevo documento técnico"""
    
    if request.method == 'POST':
        form = DocumentoTecnicoForm(request.POST, request.FILES)
        if form.is_valid():
            documento = form.save(commit=False)
            documento.autor_sistema = request.user
            documento.save()
            form.save_m2m()  # Guardar relaciones many-to-many
            
            messages.success(request, f'Documento "{documento.titulo}" creado exitosamente.')
            return redirect('capacitacion:ver-documento', documento_id=documento.id)
    else:
        form = DocumentoTecnicoForm()
    
    context = {
        'form': form,
        'titulo': 'Crear Nuevo Documento Técnico',
        'accion': 'crear',
    }
    
    return render(request, 'sistema_interno/form_documento.html', context)

@login_required
@user_passes_test(es_staff_o_admin)
def editar_documento_view(request, documento_id):
    """Vista para editar un documento técnico existente"""
    
    documento = get_object_or_404(DocumentoTecnico, id=documento_id)
    
    # Verificar permisos de edición
    if not documento.puede_editar(request.user):
        messages.error(request, 'No tienes permisos para editar este documento.')
        return redirect('capacitacion:ver-documento', documento_id=documento.id)
    
    if request.method == 'POST':
        form = DocumentoTecnicoForm(request.POST, request.FILES, instance=documento)
        if form.is_valid():
            # Registrar cambio en historial
            HistorialDocumento.objects.create(
                documento=documento,
                usuario=request.user,
                accion='editar',
                descripcion=f'Documento editado: {documento.titulo}',
                version_anterior=documento.version,
            )
            
            form.save()
            
            messages.success(request, f'Documento "{documento.titulo}" actualizado exitosamente.')
            return redirect('capacitacion:ver-documento', documento_id=documento.id)
    else:
        form = DocumentoTecnicoForm(instance=documento)
    
    context = {
        'form': form,
        'documento': documento,
        'titulo': f'Editar Documento: {documento.titulo}',
        'accion': 'editar',
    }
    
    return render(request, 'sistema_interno/form_documento.html', context)

@login_required
@user_passes_test(es_staff_o_admin)
def eliminar_documento_view(request, documento_id):
    """Vista para eliminar un documento técnico"""
    
    documento = get_object_or_404(DocumentoTecnico, id=documento_id)
    
    # Verificar permisos de eliminación
    if not documento.puede_eliminar(request.user):
        messages.error(request, 'No tienes permisos para eliminar este documento.')
        return redirect('capacitacion:ver-documento', documento_id=documento.id)
    
    if request.method == 'POST':
        titulo = documento.titulo
        
        # Registrar eliminación en historial antes de eliminar
        HistorialDocumento.objects.create(
            documento=documento,
            usuario=request.user,
            accion='eliminar',
            descripcion=f'Documento eliminado: {titulo}',
        )
        
        documento.delete()
        
        messages.success(request, f'Documento "{titulo}" eliminado exitosamente.')
        return redirect('capacitacion:documentos-tecnicos')
    
    context = {
        'documento': documento,
    }
    
    return render(request, 'sistema_interno/confirmar_eliminar_documento.html', context)

@login_required
@require_POST
def descargar_documento_view(request, documento_id):
    """Vista para manejar descarga real de documentos"""
    
    documento = get_object_or_404(DocumentoTecnico, id=documento_id, estado='publicado')
    
    # Verificar permisos
    if not documento.puede_descargar(request.user):
        messages.error(request, 'No tienes permisos para descargar este documento.')
        return redirect('capacitacion:ver-documento', documento_id=documento.id)
    
    # Incrementar contador de descargas y registrar
    documento.incrementar_descarga(request.user)
    
    # ✅ DESCARGA REAL DEL ARCHIVO
    if documento.archivo_principal and os.path.exists(documento.archivo_principal.path):
        try:
            # Obtener el archivo
            archivo_path = documento.archivo_principal.path
            
            # Detectar tipo de contenido
            content_type, _ = mimetypes.guess_type(archivo_path)
            if not content_type:
                content_type = 'application/octet-stream'
            
            # Leer el archivo
            with open(archivo_path, 'rb') as archivo:
                response = HttpResponse(archivo.read(), content_type=content_type)
                
                # Configurar headers para descarga
                filename = f"{documento.titulo}_v{documento.version}.{documento.formato}"
                # Limpiar caracteres especiales del nombre
                filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
                
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                response['Content-Length'] = os.path.getsize(archivo_path)
                
                return response
                
        except Exception as e:
            messages.error(request, f'Error al descargar el archivo: {str(e)}')
            return redirect('capacitacion:ver-documento', documento_id=documento.id)
    
    # Si no hay archivo físico, crear archivo de demostración
    else:
        # ✅ GENERAR ARCHIVO PDF DE DEMOSTRACIÓN
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.units import inch
            from io import BytesIO
            
            # Crear PDF en memoria
            buffer = BytesIO()
            p = canvas.Canvas(buffer, pagesize=letter)
            width, height = letter
            
            # Encabezado
            p.setFont("Helvetica-Bold", 20)
            p.drawString(50, height - 50, f"DOCUMENTO TÉCNICO")
            
            # Título del documento
            p.setFont("Helvetica-Bold", 16)
            y_position = height - 100
            p.drawString(50, y_position, f"Título: {documento.titulo}")
            
            # Información del documento
            p.setFont("Helvetica", 12)
            y_position -= 40
            info_lines = [
                f"Tipo: {documento.get_tipo_display()}",
                f"Categoría: {documento.categoria.nombre}",
                f"Autor: {documento.autor_documento}",
                f"Versión: {documento.version}",
                f"Fecha de creación: {documento.fecha_creacion.strftime('%d/%m/%Y')}",
                f"Estado: {documento.get_estado_display()}",
                f"Dificultad: {documento.get_dificultad_display()}",
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
            
            # Dividir descripción en líneas
            descripcion = documento.descripcion or "Sin descripción disponible."
            words = descripcion.split()
            lines = []
            current_line = ""
            
            for word in words:
                if len(current_line + " " + word) < 80:  # Aproximadamente 80 caracteres por línea
                    current_line += " " + word if current_line else word
                else:
                    lines.append(current_line)
                    current_line = word
            
            if current_line:
                lines.append(current_line)
            
            for line in lines[:10]:  # Máximo 10 líneas
                p.drawString(50, y_position, line)
                y_position -= 15
                if y_position < 100:  # Si llegamos cerca del final de la página
                    break
            
            # Objetivos si existen
            if documento.objetivos:
                y_position -= 30
                if y_position > 150:
                    p.setFont("Helvetica-Bold", 14)
                    p.drawString(50, y_position, "OBJETIVOS:")
                    
                    y_position -= 25
                    p.setFont("Helvetica", 11)
                    
                    objetivos = documento.objetivos_lista
                    for i, objetivo in enumerate(objetivos[:5]):  # Máximo 5 objetivos
                        if y_position > 100:
                            p.drawString(50, y_position, f"• {objetivo}")
                            y_position -= 15
            
            # Pie de página
            p.setFont("Helvetica-Italic", 10)
            p.drawString(50, 50, f"Sistema de Gestión de Documentos Técnicos - Lab Metal Mecánica EMI")
            p.drawString(50, 35, f"Generado el {timezone.now().strftime('%d/%m/%Y %H:%M')} por {request.user.get_full_name() or request.user.username}")
            
            # Finalizar PDF
            p.showPage()
            p.save()
            
            # Preparar respuesta
            buffer.seek(0)
            response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
            
            filename = f"{documento.titulo}_v{documento.version}.pdf"
            filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
            
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        except ImportError:
            # Si no está instalado reportlab, crear archivo de texto simple
            contenido = f"""DOCUMENTO TÉCNICO
===============

Título: {documento.titulo}
Tipo: {documento.get_tipo_display()}
Categoría: {documento.categoria.nombre}
Autor: {documento.autor_documento}
Versión: {documento.version}
Fecha: {documento.fecha_creacion.strftime('%d/%m/%Y')}

DESCRIPCIÓN:
{documento.descripcion or 'Sin descripción disponible.'}

OBJETIVOS:
{chr(10).join([f"• {obj}" for obj in documento.objetivos_lista]) if documento.objetivos_lista else 'No especificados'}

---
Generado por: {request.user.get_full_name() or request.user.username}
Fecha de descarga: {timezone.now().strftime('%d/%m/%Y %H:%M')}
Sistema de Gestión de Documentos Técnicos - Lab Metal Mecánica EMI
"""
            
            response = HttpResponse(contenido, content_type='text/plain; charset=utf-8')
            filename = f"{documento.titulo}_v{documento.version}.txt"
            filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
        
        except Exception as e:
            messages.error(request, f'Error al generar el archivo: {str(e)}')
            return redirect('capacitacion:ver-documento', documento_id=documento.id)

# ✅ AGREGAR LA VISTA QUE FALTABA: valorar_documento_view
@login_required
@require_POST
def valorar_documento_view(request, documento_id):
    """Vista para valorar un documento técnico"""
    
    documento = get_object_or_404(DocumentoTecnico, id=documento_id, estado='publicado')
    
    # Verificar si ya valoró este documento
    valoracion_existente = ValoracionDocumento.objects.filter(
        documento=documento,
        usuario=request.user
    ).first()
    
    if valoracion_existente:
        messages.warning(request, 'Ya has valorado este documento anteriormente.')
        return redirect('capacitacion:ver-documento', documento_id=documento.id)
    
    # Procesar la valoración
    valoracion = request.POST.get('valoracion')
    comentario = request.POST.get('comentario', '')
    
    if valoracion and valoracion.isdigit() and 1 <= int(valoracion) <= 5:
        ValoracionDocumento.objects.create(
            documento=documento,
            usuario=request.user,
            valoracion=int(valoracion),
            comentario=comentario
        )
        
        messages.success(request, f'Gracias por valorar este documento con {valoracion} estrellas.')
    else:
        messages.error(request, 'Valoración inválida. Debe ser entre 1 y 5 estrellas.')
    
    return redirect('capacitacion:ver-documento', documento_id=documento.id)

# ✅ AGREGAR VISTA ADICIONAL PARA GESTIONAR DOCUMENTOS
@login_required
@user_passes_test(es_staff_o_admin)
def gestionar_documentos_view(request):
    """Vista para gestionar todos los documentos técnicos"""
    
    # Obtener todos los documentos (incluyendo borradores)
    documentos = DocumentoTecnico.objects.all().select_related(
        'categoria', 'autor_sistema'
    ).order_by('-fecha_modificacion')
    
    # Filtros
    estado_filtro = request.GET.get('estado', '')
    categoria_filtro = request.GET.get('categoria', '')
    autor_filtro = request.GET.get('autor', '')
    busqueda = request.GET.get('busqueda', '')
    
    if estado_filtro:
        documentos = documentos.filter(estado=estado_filtro)
    
    if categoria_filtro:
        documentos = documentos.filter(categoria_id=categoria_filtro)
    
    if autor_filtro:
        documentos = documentos.filter(autor_sistema_id=autor_filtro)
    
    if busqueda:
        documentos = documentos.filter(
            Q(titulo__icontains=busqueda) |
            Q(autor_documento__icontains=busqueda) |
            Q(codigo_documento__icontains=busqueda)
        )
    
    # Paginación
    paginator = Paginator(documentos, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estadísticas para administradores
    stats_admin = {
        'total_documentos': DocumentoTecnico.objects.count(),
        'publicados': DocumentoTecnico.objects.filter(estado='publicado').count(),
        'borradores': DocumentoTecnico.objects.filter(estado='borrador').count(),
        'en_revision': DocumentoTecnico.objects.filter(estado='revision').count(),
        'obsoletos': DocumentoTecnico.objects.filter(estado='obsoleto').count(),
        'por_vencer': DocumentoTecnico.objects.filter(
            fecha_vencimiento__lte=timezone.now().date() + timezone.timedelta(days=30)
        ).count(),
    }
    
    context = {
        'documentos': page_obj,
        'page_obj': page_obj,
        'stats_admin': stats_admin,
        'estado_filtro': estado_filtro,
        'categoria_filtro': categoria_filtro,
        'autor_filtro': autor_filtro,
        'busqueda': busqueda,
        'categorias': CategoriaCapacitacion.objects.filter(activo=True),
        'estados': DocumentoTecnico.ESTADO_CHOICES,
        'autores': User.objects.filter(documentos_tecnicos_creados__isnull=False).distinct(),
    }
    
    return render(request, 'sistema_interno/gestionar_documentos.html', context)

# ✅ API PARA DOCUMENTOS TÉCNICOS
@login_required
def api_documento_stats(request, documento_id):
    """API para obtener estadísticas de un documento"""
    documento = get_object_or_404(DocumentoTecnico, id=documento_id)
    
    stats = {
        'vistas': documento.vistas,
        'descargas': documento.descargas,
        'valoracion_promedio': float(documento.valoracion_promedio),
        'total_valoraciones': documento.valoraciones.count(),
        'tamaño_archivo': documento.tamaño_archivo,
        'fecha_modificacion': documento.fecha_modificacion.isoformat(),
    }
    
    return JsonResponse({'success': True, 'stats': stats})