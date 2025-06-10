from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg, Sum
from django.core.paginator import Paginator
from datetime import date, timedelta
from .models import PlanMantenimiento, TareaMantenimiento, RepuestoCritico
from .forms import PlanMantenimientoForm, TareaMantenimientoForm
from apps.equipos.models import Equipo

@login_required
def planes_mantenimiento_view(request):
    """Vista principal de planes de mantenimiento con métricas mejoradas"""
    
    # Filtros
    tipo_filtro = request.GET.get('tipo', '')
    estado_filtro = request.GET.get('estado', '')
    prioridad_filtro = request.GET.get('prioridad', '')
    search = request.GET.get('search', '')
    
    # Query base
    planes = PlanMantenimiento.objects.select_related('equipo', 'responsable_principal').prefetch_related('repuestos_criticos').all()
    
    # Aplicar filtros
    if tipo_filtro:
        planes = planes.filter(tipo_mantenimiento=tipo_filtro)
    
    if estado_filtro:
        planes = planes.filter(estado=estado_filtro)
    
    if prioridad_filtro:
        planes = planes.filter(prioridad=prioridad_filtro)
    
    if search:
        planes = planes.filter(
            Q(nombre__icontains=search) |
            Q(codigo_plan__icontains=search) |
            Q(equipo__nombre__icontains=search) |
            Q(equipo__codigo_interno__icontains=search)
        )
    
    # Estadísticas básicas
    total_planes = planes.count()
    planes_activos = planes.filter(estado='activo').count()
    planes_atrasados = sum(1 for plan in planes if plan.esta_atrasado())
    planes_proximos = planes.filter(
        proxima_ejecucion__lte=date.today() + timedelta(days=7),
        estado='activo'
    ).count()
    
    # *** NUEVAS MÉTRICAS DE EFICIENCIA ***
    # Eficiencia promedio del sistema
    eficiencia_promedio = planes.aggregate(
        promedio=Avg('eficiencia_promedio')
    )['promedio'] or 0
    
    # Tasa de cumplimiento promedio
    cumplimiento_promedio = planes.aggregate(
        promedio=Avg('tasa_cumplimiento')
    )['promedio'] or 0
    
    # Planes que cumplen ISO
    planes_iso_compliant = planes.filter(cumple_iso=True).count()
    
    # MTBF promedio
    mtbf_promedio = planes.aggregate(
        promedio=Avg('mtbf')
    )['promedio'] or 0
    
    # Repuestos críticos totales
    total_repuestos_criticos = RepuestoCritico.objects.count()
    
    # Paginación
    paginator = Paginator(planes, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Calcular estados dinámicos para cada plan
    for plan in page_obj:
        plan.dias_restantes = plan.dias_hasta_mantenimiento()
        plan.atrasado = plan.esta_atrasado()
    
    context = {
        'page_obj': page_obj,
        'planes': page_obj,
        'total_planes': total_planes,
        'planes_activos': planes_activos,
        'planes_atrasados': planes_atrasados,
        'planes_proximos': planes_proximos,
        'eficiencia_promedio': round(eficiencia_promedio, 1),
        'cumplimiento_promedio': round(cumplimiento_promedio, 1),
        'planes_iso_compliant': planes_iso_compliant,
        'mtbf_promedio': round(mtbf_promedio, 1),
        'total_repuestos_criticos': total_repuestos_criticos,
        'tipo_filtro': tipo_filtro,
        'estado_filtro': estado_filtro,
        'prioridad_filtro': prioridad_filtro,
        'search': search,
        'tipos_mantenimiento': PlanMantenimiento.TIPO_MANTENIMIENTO_CHOICES,
        'estados': PlanMantenimiento.ESTADO_CHOICES,
        'prioridades': PlanMantenimiento.PRIORIDAD_CHOICES,
    }
    
    return render(request, 'sistema_interno/planes_mantenimiento.html', context)

@login_required
def crear_plan_view(request):
    """Vista para crear nuevo plan de mantenimiento industrial"""
    
    if request.method == 'POST':
        form = PlanMantenimientoForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                plan = form.save(commit=False)
                # Asignar el usuario actual como responsable si no se especificó otro
                if not plan.responsable_principal:
                    plan.responsable_principal = request.user
                
                plan.save()
                form.save_m2m()  # Guardar relaciones many-to-many
                
                messages.success(
                    request, 
                    f'✅ Plan de mantenimiento "{plan.codigo_plan} - {plan.nombre}" creado exitosamente.'
                )
                
                # Crear tareas básicas automáticamente según el tipo de mantenimiento
                crear_tareas_basicas(plan)
                
                messages.info(
                    request,
                    f'📋 Se han creado {plan.tareas.count()} tareas básicas para el plan.'
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
        'total_equipos': Equipo.objects.exclude(estado='FUERA_SERVICIO').count(),
        'total_repuestos': RepuestoCritico.objects.count(),
        'planes_activos': PlanMantenimiento.objects.filter(estado='activo').count(),
    }
    
    context = {
        'form': form,
        'accion': 'crear',
        'titulo': 'Crear Plan de Mantenimiento Industrial',
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
    """Vista para listar todas las tareas de mantenimiento"""
    tareas = TareaMantenimiento.objects.select_related('plan', 'responsable').all()
    
    # Filtros básicos
    plan_filtro = request.GET.get('plan', '')
    estado_filtro = request.GET.get('estado', '')
    
    if plan_filtro:
        tareas = tareas.filter(plan_id=plan_filtro)
    
    if estado_filtro:
        tareas = tareas.filter(estado=estado_filtro)
    
    # Paginación
    paginator = Paginator(tareas, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'tareas': page_obj,
        'planes': PlanMantenimiento.objects.filter(estado='activo'),
        'estados_tarea': TareaMantenimiento.ESTADO_TAREA_CHOICES,
        'plan_filtro': plan_filtro,
        'estado_filtro': estado_filtro,
    }
    
    return render(request, 'sistema_interno/tareas_mantenimiento.html', context)

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
        form = TareaMantenimientoForm()
    
    context = {
        'form': form,
        'plan': plan,
        'titulo': f'Crear Tarea - {plan.codigo_plan}',
    }
    
    return render(request, 'sistema_interno/crear_tarea.html', context)
