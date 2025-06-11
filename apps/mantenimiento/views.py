from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg, Sum
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models
from datetime import date, timedelta
from .models import PlanMantenimiento, TareaMantenimiento, RepuestoCritico, OrdenTrabajo
from .forms import PlanMantenimientoForm, TareaMantenimientoForm, OrdenTrabajoForm, OrdenTrabajoUpdateForm
from apps.equipos.models import Equipo

import json
import random
from django.core.serializers.json import DjangoJSONEncoder
from datetime import datetime, timedelta
from django.db.models import Count, Avg, Sum, F, Q, Case, When, IntegerField
from django.db.models.functions import TruncMonth, TruncWeek

@login_required
def planes_mantenimiento_view(request):
    """Vista completa para planes de mantenimiento"""
    
    # Filtros
    search = request.GET.get('search', '')
    tipo_filtro = request.GET.get('tipo', '')
    estado_filtro = request.GET.get('estado', '')
    prioridad_filtro = request.GET.get('prioridad', '')
    normativa_filtro = request.GET.get('normativa', '')
    temporal_filtro = request.GET.get('temporal', '')
    
    # Query base
    planes = PlanMantenimiento.objects.select_related('equipo', 'responsable_principal').all()
    
    # Aplicar filtros
    if search:
        planes = planes.filter(
            Q(nombre__icontains=search) |
            Q(codigo_plan__icontains=search) |
            Q(equipo__nombre__icontains=search) |
            Q(equipo__codigo_interno__icontains=search) |
            Q(descripcion__icontains=search)
        )
    
    if tipo_filtro:
        planes = planes.filter(tipo_mantenimiento=tipo_filtro)
    
    if estado_filtro:
        planes = planes.filter(estado=estado_filtro)
    
    if prioridad_filtro:
        planes = planes.filter(prioridad=prioridad_filtro)
    
    if normativa_filtro:
        planes = planes.filter(norma_aplicable=normativa_filtro)
    
    # Filtro temporal
    if temporal_filtro:
        hoy = date.today()
        if temporal_filtro == 'atrasado':
            planes = planes.filter(proxima_ejecucion__lt=hoy)
        elif temporal_filtro == 'proximo':
            planes = planes.filter(proxima_ejecucion__lte=hoy + timedelta(days=7), proxima_ejecucion__gte=hoy)
        elif temporal_filtro == 'mes':
            planes = planes.filter(proxima_ejecucion__lte=hoy + timedelta(days=30), proxima_ejecucion__gte=hoy)
    
    # Calcular métricas para cada plan
    for plan in planes:
        plan.dias_restantes = plan.dias_hasta_mantenimiento()
        plan.atrasado = plan.esta_atrasado()
    
    # Estadísticas
    total_planes = planes.count()
    planes_activos = planes.filter(estado='activo').count()
    planes_atrasados = planes.filter(proxima_ejecucion__lt=date.today()).count()
    planes_proximos = planes.filter(
        proxima_ejecucion__lte=date.today() + timedelta(days=7),
        proxima_ejecucion__gte=date.today()
    ).count()
    
    # Eficiencia promedio
    eficiencia_promedio = planes.aggregate(promedio=Avg('eficiencia_promedio'))['promedio'] or 0
    
    # Cumplimiento promedio
    cumplimiento_promedio = planes.aggregate(promedio=Avg('tasa_cumplimiento'))['promedio'] or 0
    
    # Planes ISO compliant
    planes_iso_compliant = planes.filter(cumple_iso=True).count()
    
    # Total repuestos críticos
    total_repuestos_criticos = RepuestoCritico.objects.count()
    
    # Paginación
    paginator = Paginator(planes, 12)  # 12 planes por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'planes': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'search': search,
        'tipo_filtro': tipo_filtro,
        'estado_filtro': estado_filtro,
        'prioridad_filtro': prioridad_filtro,
        'normativa_filtro': normativa_filtro,
        'temporal_filtro': temporal_filtro,
        
        # Opciones para filtros
        'tipos_mantenimiento': PlanMantenimiento.TIPO_MANTENIMIENTO_CHOICES,
        'estados': PlanMantenimiento.ESTADO_CHOICES,
        'prioridades': PlanMantenimiento.PRIORIDAD_CHOICES,
        'normativas': PlanMantenimiento.NORMAS_APLICABLES_CHOICES,
        
        # Estadísticas
        'total_planes': total_planes,
        'planes_activos': planes_activos,
        'planes_atrasados': planes_atrasados,
        'planes_proximos': planes_proximos,
        'eficiencia_promedio': round(eficiencia_promedio, 1),
        'cumplimiento_promedio': round(cumplimiento_promedio, 1),
        'planes_iso_compliant': planes_iso_compliant,
        'total_repuestos_criticos': total_repuestos_criticos,
        
        'titulo': 'Planes de Mantenimiento',
    }
    
    return render(request, 'sistema_interno/planes_mantenimiento.html', context)

@login_required
def crear_plan_view(request):
    """Vista para crear plan de mantenimiento"""
    
    if request.method == 'POST':
        form = PlanMantenimientoForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                plan = form.save()
                
                # Crear tareas básicas automáticamente
                crear_tareas_basicas(plan)
                
                messages.success(
                    request, 
                    f'✅ Plan "{plan.codigo_plan} - {plan.nombre}" creado exitosamente con tareas básicas.'
                )
                
                return redirect('mantenimiento:plan-detalle', pk=plan.pk)
                
            except Exception as e:
                messages.error(
                    request, 
                    f'❌ Error al crear el plan: {str(e)}'
                )
        else:
            messages.error(
                request, 
                '❌ Error en el formulario. Por favor revise los campos marcados en rojo.'
            )
    else:
        form = PlanMantenimientoForm()
    
    # Estadísticas para el contexto
    stats = {
        'total_planes': PlanMantenimiento.objects.count(),
        'total_equipos': Equipo.objects.exclude(estado='FUERA_SERVICIO').count(),
        'planes_activos': PlanMantenimiento.objects.filter(estado='activo').count(),
    }
    
    context = {
        'form': form,
        'accion': 'crear',
        'titulo': 'Crear Plan de Mantenimiento',
        'stats': stats,
    }
    
    return render(request, 'sistema_interno/crear_plan.html', context)

@login_required
def editar_plan_view(request, pk):
    """Vista para editar plan de mantenimiento existente"""
    
    plan = get_object_or_404(PlanMantenimiento, pk=pk)
    
    if request.method == 'POST':
        form = PlanMantenimientoForm(request.POST, request.FILES, instance=plan)
        if form.is_valid():
            try:
                plan = form.save()
                
                messages.success(
                    request, 
                    f'✅ Plan "{plan.codigo_plan} - {plan.nombre}" actualizado exitosamente.'
                )
                
                return redirect('mantenimiento:plan-detalle', pk=plan.pk)
                
            except Exception as e:
                messages.error(
                    request, 
                    f'❌ Error al actualizar el plan: {str(e)}'
                )
        else:
            messages.error(
                request, 
                '❌ Error en el formulario. Por favor revise los campos marcados en rojo.'
            )
    else:
        form = PlanMantenimientoForm(instance=plan)
    
    context = {
        'form': form,
        'plan': plan,
        'accion': 'editar',
        'titulo': f'Editar Plan - {plan.codigo_plan}',
    }
    
    return render(request, 'sistema_interno/crear_plan.html', context)

@login_required
def detalle_plan_view(request, pk):
    """Vista detallada del plan de mantenimiento"""
    
    plan = get_object_or_404(PlanMantenimiento, pk=pk)
    tareas = plan.tareas.all().order_by('orden')
    
    # Calcular métricas
    plan.dias_restantes = plan.dias_hasta_mantenimiento()
    plan.atrasado = plan.esta_atrasado()
    
    context = {
        'plan': plan,
        'tareas': tareas,
    }
    
    return render(request, 'sistema_interno/plan_detalle.html', context)

@login_required
def eliminar_plan_view(request, pk):
    """Vista para eliminar plan de mantenimiento"""
    
    plan = get_object_or_404(PlanMantenimiento, pk=pk)
    
    if request.method == 'POST':
        nombre = plan.nombre
        plan.delete()
        messages.success(request, f'Plan de mantenimiento "{nombre}" eliminado exitosamente.')
        return redirect('mantenimiento:planes-mantenimiento')
    
    context = {
        'plan': plan,
    }
    
    return render(request, 'sistema_interno/plan_confirmar_eliminar.html', context)

def crear_tareas_basicas(plan):
    """Crear tareas básicas automáticamente según el tipo de mantenimiento"""
    
    tareas_por_tipo = {
        'preventivo': [
            {
                'nombre': 'Inspección visual general',
                'descripcion': 'Revisión visual completa del equipo según procedimientos ISO',
                'duracion_estimada': 30,
                'es_critica': True,
                'requiere_verificacion': True,
                'orden': 1
            },
            {
                'nombre': 'Verificación de parámetros operacionales',
                'descripcion': 'Medición y registro de parámetros de operación',
                'duracion_estimada': 45,
                'es_critica': True,
                'requiere_verificacion': True,
                'orden': 2
            },
            {
                'nombre': 'Lubricación y engrase',
                'descripcion': 'Aplicación de lubricantes según especificaciones',
                'duracion_estimada': 60,
                'es_critica': False,
                'requiere_verificacion': False,
                'orden': 3
            },
            {
                'nombre': 'Limpieza y mantenimiento básico',
                'descripcion': 'Limpieza general y mantenimiento preventivo',
                'duracion_estimada': 30,
                'es_critica': False,
                'requiere_verificacion': False,
                'orden': 4
            },
        ],
        'correctivo': [
            {
                'nombre': 'Diagnóstico de falla',
                'descripcion': 'Identificación y análisis de la falla reportada',
                'duracion_estimada': 60,
                'es_critica': True,
                'requiere_verificacion': True,
                'orden': 1
            },
            {
                'nombre': 'Desmontaje y análisis',
                'descripcion': 'Desmontaje de componentes para análisis detallado',
                'duracion_estimada': 90,
                'es_critica': True,
                'requiere_verificacion': True,
                'orden': 2
            },
            {
                'nombre': 'Reparación o reemplazo',
                'descripcion': 'Reparación o reemplazo de componentes defectuosos',
                'duracion_estimada': 120,
                'es_critica': True,
                'requiere_verificacion': True,
                'orden': 3
            },
            {
                'nombre': 'Pruebas funcionales',
                'descripcion': 'Verificación del funcionamiento correcto post-reparación',
                'duracion_estimada': 45,
                'es_critica': True,
                'requiere_verificacion': True,
                'orden': 4
            },
        ],
        'predictivo': [
            {
                'nombre': 'Análisis de vibraciones',
                'descripcion': 'Medición y análisis de vibraciones del equipo',
                'duracion_estimada': 45,
                'es_critica': True,
                'requiere_verificacion': True,
                'orden': 1
            },
            {
                'nombre': 'Termografía infrarroja',
                'descripcion': 'Inspección termográfica para detección de anomalías',
                'duracion_estimada': 30,
                'es_critica': True,
                'requiere_verificacion': True,
                'orden': 2
            },
            {
                'nombre': 'Análisis de aceites',
                'descripcion': 'Toma de muestras y análisis de lubricantes',
                'duracion_estimada': 20,
                'es_critica': False,
                'requiere_verificacion': True,
                'orden': 3
            },
            {
                'nombre': 'Registro y análisis de datos',
                'descripcion': 'Procesamiento y análisis de datos recopilados',
                'duracion_estimada': 60,
                'es_critica': False,
                'requiere_verificacion': False,
                'orden': 4
            },
        ],
        'autonomo': [
            {
                'nombre': 'Inspección diaria del operador',
                'descripcion': 'Revisión rutinaria a cargo del operador del equipo',
                'duracion_estimada': 15,
                'es_critica': False,
                'requiere_verificacion': False,
                'orden': 1
            },
            {
                'nombre': 'Limpieza básica',
                'descripcion': 'Limpieza externa y áreas accesibles',
                'duracion_estimada': 20,
                'es_critica': False,
                'requiere_verificacion': False,
                'orden': 2
            },
            {
                'nombre': 'Verificación de niveles',
                'descripcion': 'Verificación de niveles de fluidos y lubricantes',
                'duracion_estimada': 10,
                'es_critica': False,
                'requiere_verificacion': False,
                'orden': 3
            },
        ]
    }
    
    tareas_a_crear = tareas_por_tipo.get(plan.tipo_mantenimiento, [])
    
    for tarea_data in tareas_a_crear:
        TareaMantenimiento.objects.create(
            plan=plan,
            **tarea_data
        )

@login_required
def tareas_view(request):
    """Vista para tareas de mantenimiento"""
    # Obtener filtros
    plan_filtro = request.GET.get('plan')
    estado_filtro = request.GET.get('estado')
    
    # Query base
    tareas = TareaMantenimiento.objects.select_related('plan', 'responsable').all()
    
    # Aplicar filtros
    if plan_filtro:
        tareas = tareas.filter(plan_id=plan_filtro)
    
    if estado_filtro:
        tareas = tareas.filter(estado=estado_filtro)
    
    # Ordenar por plan y orden
    tareas = tareas.order_by('plan__codigo_plan', 'orden')
    
    # Obtener datos para filtros
    planes = PlanMantenimiento.objects.all().order_by('codigo_plan')
    estados_tarea = TareaMantenimiento.ESTADO_TAREA_CHOICES
    
    # Verificar si viene de un plan específico
    plan_seleccionado = None
    if plan_filtro:
        try:
            plan_seleccionado = PlanMantenimiento.objects.get(id=plan_filtro)
        except PlanMantenimiento.DoesNotExist:
            pass
    
    # Paginación
    paginator = Paginator(tareas, 20)  # 20 tareas por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'titulo': 'Tareas de Mantenimiento',
        'tareas': page_obj,
        'page_obj': page_obj,
        'total_tareas': tareas.count(),
        'planes': planes,
        'estados_tarea': estados_tarea,
        'plan_filtro': plan_filtro,
        'estado_filtro': estado_filtro,
        'plan_seleccionado': plan_seleccionado,
    }
    
    return render(request, 'sistema_interno/tareas_mantenimiento.html', context)

@login_required
def ordenes_trabajo_view(request):
    """Vista para órdenes de trabajo"""
    
    # Filtros
    estado_filtro = request.GET.get('estado', '')
    prioridad_filtro = request.GET.get('prioridad', '')
    asignado_filtro = request.GET.get('asignado', '')
    search = request.GET.get('search', '')
    
    # Query base
    ordenes = OrdenTrabajo.objects.select_related('equipo', 'solicitante', 'asignado_a', 'plan_mantenimiento').all()
    
    # Aplicar filtros
    if estado_filtro:
        ordenes = ordenes.filter(estado=estado_filtro)
    
    if prioridad_filtro:
        ordenes = ordenes.filter(prioridad=prioridad_filtro)
    
    if asignado_filtro:
        ordenes = ordenes.filter(asignado_a_id=asignado_filtro)
    
    if search:
        ordenes = ordenes.filter(
            Q(numero_orden__icontains=search) |
            Q(titulo__icontains=search) |
            Q(descripcion__icontains=search) |
            Q(equipo__nombre__icontains=search) |
            Q(equipo__codigo_interno__icontains=search)
        )
    
    # Calcular métricas para cada orden
    for orden in ordenes:
        orden.atrasada = orden.esta_atrasada()
        orden.eficiencia = orden.get_eficiencia()
        orden.duracion = orden.calcular_duracion()
    
    # Estadísticas
    total_ordenes = ordenes.count()
    ordenes_pendientes = ordenes.filter(estado='pendiente').count()
    ordenes_progreso = ordenes.filter(estado='en_progreso').count()
    ordenes_completadas = ordenes.filter(estado='completada').count()
    ordenes_atrasadas = sum(1 for orden in ordenes if orden.esta_atrasada())
    
    # Eficiencia promedio
    eficiencia_promedio = 0
    ordenes_con_eficiencia = [orden for orden in ordenes if orden.get_eficiencia() > 0]
    if ordenes_con_eficiencia:
        eficiencia_promedio = sum(orden.get_eficiencia() for orden in ordenes_con_eficiencia) / len(ordenes_con_eficiencia)
    
    # Paginación
    paginator = Paginator(ordenes, 12)  # 12 órdenes por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'ordenes': page_obj,
        'page_obj': page_obj,
        'search': search,
        'estado_filtro': estado_filtro,
        'prioridad_filtro': prioridad_filtro,
        'asignado_filtro': asignado_filtro,
        
        # Opciones para filtros
        'estados': OrdenTrabajo.ESTADO_CHOICES,
        'prioridades': OrdenTrabajo.PRIORIDAD_CHOICES,
        'usuarios': User.objects.filter(is_active=True),
        
        # Estadísticas
        'total_ordenes': total_ordenes,
        'ordenes_pendientes': ordenes_pendientes,
        'ordenes_progreso': ordenes_progreso,
        'ordenes_completadas': ordenes_completadas,
        'ordenes_atrasadas': ordenes_atrasadas,
        'eficiencia_promedio': round(eficiencia_promedio, 1),
        
        'titulo': 'Órdenes de Trabajo',
    }
    
    return render(request, 'sistema_interno/ordenes_de_trabajo.html', context)

@login_required
def crear_orden_view(request):
    """Vista para crear nueva orden de trabajo"""
    
    if request.method == 'POST':
        form = OrdenTrabajoForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                orden = form.save(commit=False)
                orden.solicitante = request.user
                orden.save()
                
                messages.success(
                    request, 
                    f'✅ Orden de trabajo "{orden.numero_orden}" creada exitosamente.'
                )
                
                return redirect('mantenimiento:orden-detalle', pk=orden.pk)
                
            except Exception as e:
                messages.error(
                    request, 
                    f'❌ Error al crear la orden: {str(e)}'
                )
        else:
            messages.error(
                request, 
                '❌ Error en el formulario. Por favor revise los campos marcados.'
            )
    else:
        form = OrdenTrabajoForm()
    
    context = {
        'form': form,
        'titulo': 'Crear Orden de Trabajo',
        'accion': 'crear',
    }
    
    return render(request, 'sistema_interno/crear_orden.html', context)

@login_required
def detalle_orden_view(request, pk):
    """Vista detallada de la orden de trabajo"""
    
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    
    # Calcular métricas
    orden.atrasada = orden.esta_atrasada()
    orden.eficiencia = orden.get_eficiencia()
    orden.duracion = orden.calcular_duracion()
    
    context = {
        'orden': orden,
    }
    
    return render(request, 'sistema_interno/orden_detalle.html', context)

@login_required
def actualizar_orden_view(request, pk):
    """Vista para actualizar el progreso de una orden de trabajo"""
    
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    
    if request.method == 'POST':
        form = OrdenTrabajoUpdateForm(request.POST, request.FILES, instance=orden)
        if form.is_valid():
            try:
                # Si se marca como completada, asignar fecha de completación
                if form.cleaned_data.get('estado') == 'completada' and not orden.fecha_completada:
                    orden.fecha_completada = timezone.now()
                
                orden = form.save()
                
                messages.success(
                    request, 
                    f'✅ Orden "{orden.numero_orden}" actualizada exitosamente.'
                )
                
                return redirect('mantenimiento:orden-detalle', pk=orden.pk)
                
            except Exception as e:
                messages.error(
                    request, 
                    f'❌ Error al actualizar la orden: {str(e)}'
                )
        else:
            messages.error(
                request, 
                '❌ Error en el formulario. Por favor revise los campos.'
            )
    else:
        form = OrdenTrabajoUpdateForm(instance=orden)
    
    context = {
        'form': form,
        'orden': orden,
        'titulo': f'Actualizar Orden - {orden.numero_orden}',
        'accion': 'actualizar',
    }
    
    return render(request, 'sistema_interno/actualizar_orden.html', context)

@login_required
def analisis_predictivo_view(request):
    """Vista de análisis predictivo de mantenimiento"""
    
    # Obtener rango de fechas (últimos 12 meses por defecto)
    fecha_fin = timezone.now().date()
    fecha_inicio = fecha_fin - timedelta(days=365)
    
    # Filtros opcionales
    equipo_filtro = request.GET.get('equipo', '')
    periodo_filtro = request.GET.get('periodo', '12')  # 3, 6, 12 meses
    
    # Ajustar rango según el período seleccionado
    if periodo_filtro == '3':
        fecha_inicio = fecha_fin - timedelta(days=90)
    elif periodo_filtro == '6':
        fecha_inicio = fecha_fin - timedelta(days=180)
    
    # Queryset base de órdenes
    ordenes_base = OrdenTrabajo.objects.filter(
        fecha_creacion__date__gte=fecha_inicio,
        fecha_creacion__date__lte=fecha_fin
    )
    
    if equipo_filtro:
        ordenes_base = ordenes_base.filter(equipo_id=equipo_filtro)
    
    # Órdenes por mes para gráfico de tendencias
    ordenes_por_mes = ordenes_base.annotate(
        mes=TruncMonth('fecha_creacion')
    ).values('mes').annotate(
        total=Count('id'),
        preventivas=Count(Case(When(tipo_orden='preventivo', then=1), output_field=IntegerField())),
        correctivas=Count(Case(When(tipo_orden='correctivo', then=1), output_field=IntegerField())),
        predictivas=Count(Case(When(tipo_orden='predictivo', then=1), output_field=IntegerField()))
    ).order_by('mes')
    
    # Convertir para JSON
    meses_labels = []
    preventivas_data = []
    correctivas_data = []
    predictivas_data = []
    
    for item in ordenes_por_mes:
        meses_labels.append(item['mes'].strftime('%b %Y'))
        preventivas_data.append(item['preventivas'])
        correctivas_data.append(item['correctivas'])
        predictivas_data.append(item['predictivas'])
    
    # Métricas generales
    total_ordenes = ordenes_base.count()
    ordenes_preventivas = ordenes_base.filter(tipo_orden='preventivo').count()
    ordenes_correctivas = ordenes_base.filter(tipo_orden='correctivo').count()
    
    # Ratio preventivo/correctivo (ideal >= 4:1)
    ratio_prev_corr = (ordenes_preventivas / ordenes_correctivas) if ordenes_correctivas > 0 else 0
    
    # MTBF promedio del sistema (simulado)
    mtbf_promedio = 2160  # 90 días en horas
    
    # Disponibilidad promedio del sistema (simulado)
    disponibilidad_promedio = 92.5
    
    # Eficiencia temporal (órdenes completadas a tiempo)
    ordenes_completadas = ordenes_base.filter(estado='completada')
    ordenes_a_tiempo = 0
    ordenes_atrasadas = 0
    
    for orden in ordenes_completadas:
        if orden.fecha_programada and orden.fecha_completada:
            if orden.fecha_completada <= orden.fecha_programada:
                ordenes_a_tiempo += 1
            else:
                ordenes_atrasadas += 1
    
    total_programadas = ordenes_a_tiempo + ordenes_atrasadas
    eficiencia_tiempo = (ordenes_a_tiempo / total_programadas * 100) if total_programadas > 0 else 0
    
    context = {
        # Métricas generales
        'total_ordenes': total_ordenes,
        'ordenes_preventivas': ordenes_preventivas,
        'ordenes_correctivas': ordenes_correctivas,
        'ratio_prev_corr': round(ratio_prev_corr, 2),
        'eficiencia_tiempo': round(eficiencia_tiempo, 1),
        'mtbf_promedio': mtbf_promedio,
        'disponibilidad_promedio': disponibilidad_promedio,
        
        # Datos para gráficos (JSON)
        'meses_labels': json.dumps(meses_labels),
        'preventivas_data': json.dumps(preventivas_data),
        'correctivas_data': json.dumps(correctivas_data),
        'predictivas_data': json.dumps(predictivas_data),
        
        # Filtros
        'equipo_filtro': equipo_filtro,
        'periodo_filtro': periodo_filtro,
        'equipos_disponibles': Equipo.objects.filter(estado='OPERATIVO'),
        
        'titulo': 'Análisis Predictivo',
    }
    
    return render(request, 'sistema_interno/analisis_predictivo.html', context)

@login_required
def crear_tarea_view(request, plan_pk):
    """Vista para crear nueva tarea de mantenimiento"""
    plan = get_object_or_404(PlanMantenimiento, pk=plan_pk)
    
    if request.method == 'POST':
        form = TareaMantenimientoForm(request.POST)
        if form.is_valid():
            tarea = form.save(commit=False)
            tarea.plan = plan
            tarea.save()
            
            messages.success(request, f'Tarea "{tarea.nombre}" creada exitosamente.')
            return redirect('mantenimiento:plan-detalle', pk=plan.pk)
        else:
            messages.error(request, 'Error al crear la tarea.')
    else:
        form = TareaMantenimientoForm()
    
    context = {
        'form': form,
        'plan': plan,
        'titulo': f'Crear Tarea - {plan.codigo_plan}',
    }
    
    return render(request, 'sistema_interno/crear_tarea.html', context)
