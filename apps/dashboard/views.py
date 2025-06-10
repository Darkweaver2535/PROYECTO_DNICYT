# Reemplazar COMPLETAMENTE el archivo views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Avg
from datetime import datetime, timedelta
from apps.equipos.models import Equipo

@login_required
def dashboard_view(request):
    """Dashboard principal con métricas dinámicas"""
    
    try:
        # Importar modelos de mantenimiento de forma segura
        from apps.mantenimiento.models import PlanMantenimiento, TareaMantenimiento, RepuestoCritico
        mantenimiento_disponible = True
    except ImportError:
        mantenimiento_disponible = False
        print("⚠️  Módulo de mantenimiento no disponible")
    
    # === MÉTRICAS DE EQUIPOS ===
    # Total de equipos
    total_equipos = Equipo.objects.count()
    
    # Equipos por estado
    equipos_activos = Equipo.objects.filter(estado='OPERATIVO').count()
    equipos_mantenimiento = Equipo.objects.filter(estado='MANTENIMIENTO').count()
    equipos_fuera_servicio = Equipo.objects.filter(estado='FUERA_SERVICIO').count()
    
    # Calcular porcentaje operativo
    porcentaje_operativo = round((equipos_activos / total_equipos * 100), 1) if total_equipos > 0 else 0
    
    # Equipos creados este mes
    inicio_mes = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    equipos_este_mes = Equipo.objects.filter(fecha_ingreso__gte=inicio_mes).count()
    
    # === MÉTRICAS DE SECCIONES ===
    # Contar secciones con equipos activos
    secciones_con_equipos = Equipo.objects.values('seccion').distinct().count()
    total_secciones_definidas = len(Equipo.SECCION_CHOICES)
    porcentaje_cobertura_secciones = round((secciones_con_equipos / total_secciones_definidas * 100), 1) if total_secciones_definidas > 0 else 0
    
    # === MÉTRICAS DE MANTENIMIENTO ===
    if mantenimiento_disponible:
        # Planes de mantenimiento activos
        planes_activos = PlanMantenimiento.objects.filter(estado='activo').count()
        
        # Total de planes
        total_planes = PlanMantenimiento.objects.count()
        
        # Mantenimientos ejecutados este mes
        mantenimientos_este_mes = PlanMantenimiento.objects.filter(
            ultima_ejecucion__gte=inicio_mes
        ).count() if PlanMantenimiento.objects.filter(ultima_ejecucion__isnull=False).exists() else 0
        
        # Eficiencia promedio de mantenimientos
        eficiencia_promedio = PlanMantenimiento.objects.filter(
            estado='activo'
        ).aggregate(
            promedio=Avg('eficiencia_promedio')
        )['promedio'] or 0
        
        # CORREGIR: Cambio vs mes anterior (usar fecha_creacion en lugar de fecha_actualizacion_ficha)
        inicio_mes_anterior = (inicio_mes - timedelta(days=32)).replace(day=1)
        fin_mes_anterior = inicio_mes - timedelta(days=1)
        
        eficiencia_mes_anterior = PlanMantenimiento.objects.filter(
            fecha_creacion__range=[inicio_mes_anterior, fin_mes_anterior],  # ← CORREGIDO
            estado='activo'
        ).aggregate(
            promedio=Avg('eficiencia_promedio')
        )['promedio'] or 0
        
        cambio_eficiencia = round(eficiencia_promedio - eficiencia_mes_anterior, 1) if eficiencia_mes_anterior > 0 else 0
        
        print(f"🔍 DEBUG Dashboard: Total planes = {total_planes}, Planes activos = {planes_activos}")
        
    else:
        planes_activos = 0
        total_planes = 0
        mantenimientos_este_mes = 0
        eficiencia_promedio = 0
        cambio_eficiencia = 0
    
    # === ALERTAS ACTIVAS ===
    alertas_count = 0
    alertas_detalle = []
    
    # Equipos fuera de servicio
    if equipos_fuera_servicio > 0:
        alertas_count += equipos_fuera_servicio
        alertas_detalle.append({
            'tipo': 'critica',
            'titulo': f'{equipos_fuera_servicio} Equipo(s) Fuera de Servicio',
            'descripcion': 'Equipos que requieren reparación urgente',
            'tiempo': 'Requiere atención inmediata'
        })
    
    # Mantenimientos atrasados (solo si el módulo está disponible)
    if mantenimiento_disponible:
        try:
            hoy = datetime.now().date()
            planes_atrasados = PlanMantenimiento.objects.filter(
                proxima_ejecucion__lt=hoy,
                estado='activo'
            ).count()
            
            if planes_atrasados > 0:
                alertas_count += planes_atrasados
                alertas_detalle.append({
                    'tipo': 'warning',
                    'titulo': f'{planes_atrasados} Mantenimiento(s) Atrasado(s)',
                    'descripcion': 'Planes de mantenimiento que superaron su fecha programada',
                    'tiempo': 'Atrasados'
                })
            
            # Mantenimientos próximos (próximos 7 días)
            fecha_limite = hoy + timedelta(days=7)
            planes_proximos = PlanMantenimiento.objects.filter(
                proxima_ejecucion__lte=fecha_limite,
                proxima_ejecucion__gte=hoy,
                estado='activo'
            ).count()
            
            if planes_proximos > 0:
                alertas_count += planes_proximos
                alertas_detalle.append({
                    'tipo': 'info',
                    'titulo': f'{planes_proximos} Mantenimiento(s) Próximo(s)',
                    'descripcion': 'Mantenimientos programados para los próximos 7 días',
                    'tiempo': 'Próximos 7 días'
                })
        except Exception as e:
            print(f"⚠️  Error calculando alertas de mantenimiento: {e}")
    
    # === ESTADO POR SECCIONES ===
    estado_secciones = []
    for seccion_code, seccion_name in Equipo.SECCION_CHOICES:
        equipos_seccion = Equipo.objects.filter(seccion=seccion_code)
        total_seccion = equipos_seccion.count()
        activos_seccion = equipos_seccion.filter(estado='OPERATIVO').count()
        
        if total_seccion > 0:
            porcentaje_seccion = round((activos_seccion / total_seccion * 100), 1)
            estado_secciones.append({
                'nombre': seccion_name,
                'activos': activos_seccion,
                'total': total_seccion,
                'porcentaje': porcentaje_seccion,
                'estado': 'success' if porcentaje_seccion >= 90 else 'warning' if porcentaje_seccion >= 70 else 'danger'
            })
    
    # === ACTIVIDAD RECIENTE ===
    actividad_reciente = []
    
    # Últimos equipos agregados
    ultimos_equipos = Equipo.objects.order_by('-fecha_ingreso')[:3]
    for equipo in ultimos_equipos:
        actividad_reciente.append({
            'tipo': 'alert',
            'titulo': 'Nuevo Equipo Agregado',
            'descripcion': f'{equipo.codigo_interno} - {equipo.nombre}',
            'tiempo': equipo.fecha_ingreso,
            'seccion': equipo.get_seccion_display()
        })
    
    # Últimos mantenimientos completados (solo si el módulo está disponible)
    if mantenimiento_disponible:
        try:
            ultimos_mantenimientos = PlanMantenimiento.objects.filter(
                ultima_ejecucion__isnull=False
            ).order_by('-ultima_ejecucion')[:2]
            
            for plan in ultimos_mantenimientos:
                actividad_reciente.append({
                    'tipo': 'maintenance',
                    'titulo': 'Mantenimiento Completado',
                    'descripcion': f'{plan.equipo.codigo_interno} - {plan.nombre}',
                    'tiempo': plan.ultima_ejecucion,
                    'seccion': plan.equipo.get_seccion_display()
                })
        except Exception as e:
            print(f"⚠️  Error obteniendo últimos mantenimientos: {e}")
    
    # Ordenar por tiempo descendente
    actividad_reciente.sort(key=lambda x: x['tiempo'], reverse=True)
    
    # === PRÓXIMOS MANTENIMIENTOS ===
    proximos_mantenimientos = []
    
    if mantenimiento_disponible:
        try:
            # Obtener TODOS los planes de mantenimiento para mostrar
            todos_los_planes = PlanMantenimiento.objects.filter(
                estado__in=['activo', 'borrador']  # Incluir tanto activos como borradores
            ).select_related('equipo').order_by('proxima_ejecucion')[:10]
            
            print(f"🔍 DEBUG: Encontrados {todos_los_planes.count()} planes para mostrar")
            
            # Si no hay proxima_ejecucion, usar fecha_inicio
            for plan in todos_los_planes:
                fecha_referencia = plan.proxima_ejecucion or plan.fecha_inicio
                hoy = datetime.now().date()
                
                if fecha_referencia:
                    # Calcular días hasta el mantenimiento
                    dias_restantes = (fecha_referencia - hoy).days
                    
                    # Asignar estado temporal y urgencia
                    if dias_restantes < 0:
                        plan.estado_temporal = f'Atrasado ({abs(dias_restantes)} días)'
                        plan.clase_urgencia = 'danger'
                    elif dias_restantes == 0:
                        plan.estado_temporal = 'Hoy'
                        plan.clase_urgencia = 'warning'
                    elif dias_restantes == 1:
                        plan.estado_temporal = 'Mañana'
                        plan.clase_urgencia = 'warning'
                    elif dias_restantes <= 7:
                        plan.estado_temporal = f'En {dias_restantes} días'
                        plan.clase_urgencia = 'info'
                    elif dias_restantes <= 30:
                        plan.estado_temporal = f'En {dias_restantes} días'
                        plan.clase_urgencia = 'secondary'
                    else:
                        plan.estado_temporal = f'En {dias_restantes} días'
                        plan.clase_urgencia = 'light'
                    
                    # Formatear fecha para mostrar
                    plan.fecha_formateada = fecha_referencia.strftime('%d/%m/%Y')
                else:
                    plan.estado_temporal = 'Sin programar'
                    plan.clase_urgencia = 'secondary'
                    plan.fecha_formateada = 'No definida'
                
                proximos_mantenimientos.append(plan)
                
            print(f"🔍 DEBUG: Procesados {len(proximos_mantenimientos)} planes para dashboard")
            
        except Exception as e:
            print(f"❌ Error obteniendo próximos mantenimientos: {e}")
            proximos_mantenimientos = []
    
    context = {
        # Métricas principales
        'total_equipos': total_equipos,
        'equipos_activos': equipos_activos,
        'equipos_mantenimiento': equipos_mantenimiento,
        'equipos_fuera_servicio': equipos_fuera_servicio,
        'porcentaje_operativo': porcentaje_operativo,
        'equipos_este_mes': equipos_este_mes,
        
        # Métricas de secciones
        'secciones_activas': secciones_con_equipos,
        'porcentaje_cobertura_secciones': porcentaje_cobertura_secciones,
        
        # Métricas de mantenimiento
        'planes_activos': planes_activos,
        'total_planes': total_planes if mantenimiento_disponible else 0,
        'mantenimientos_este_mes': mantenimientos_este_mes,
        'eficiencia_promedio': round(eficiencia_promedio, 1),
        'cambio_eficiencia': cambio_eficiencia,
        
        # Alertas
        'alertas_count': alertas_count,
        'alertas_detalle': alertas_detalle,
        
        # Estado por secciones
        'estado_secciones': estado_secciones,
        
        # Actividad y próximos mantenimientos
        'actividad_reciente': actividad_reciente[:5],
        'proximos_mantenimientos': proximos_mantenimientos,
        
        # Indicador de disponibilidad del módulo
        'mantenimiento_disponible': mantenimiento_disponible,
    }
    
    print(f"🎯 DEBUG Final: Context enviado - planes_activos={planes_activos}, proximos_mantenimientos={len(proximos_mantenimientos)}")
    
    return render(request, 'sistema_interno/dashboard.html', context)