from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from datetime import datetime, timedelta, date
from apps.equipos.models import Equipo
from apps.mantenimiento.models import PlanMantenimiento, OrdenTrabajo
import random

class Command(BaseCommand):
    help = 'Crea datos de demostración para el análisis predictivo'

    def handle(self, *args, **options):
        self.stdout.write('🔧 Creando datos de demostración...')
        
        # Crear usuario demo si no existe
        user, created = User.objects.get_or_create(
            username='demo_user',
            defaults={
                'email': 'demo@example.com',
                'first_name': 'Usuario',
                'last_name': 'Demo'
            }
        )
        
        # Crear equipos demo si no existen
        equipos_demo = [
            {'codigo': 'TOR-001', 'nombre': 'Torno CNC Principal', 'seccion': 'MAQUINADO'},
            {'codigo': 'FRE-001', 'nombre': 'Fresadora Universal', 'seccion': 'MAQUINADO'},
            {'codigo': 'SOL-001', 'nombre': 'Soldadora MIG/MAG', 'seccion': 'SOLDADURA'},
            {'codigo': 'TAL-001', 'nombre': 'Taladro de Columna', 'seccion': 'MAQUINADO'},
            {'codigo': 'ESP-001', 'nombre': 'Esmeriladora de Banco', 'seccion': 'SUJECION'},
        ]
        
        equipos = []
        for eq_data in equipos_demo:
            equipo, created = Equipo.objects.get_or_create(
                codigo_interno=eq_data['codigo'],
                defaults={
                    'nombre': eq_data['nombre'],
                    'seccion': eq_data['seccion'],
                    'estado': 'OPERATIVO',
                    'ubicacion_fisica': f'Área {eq_data["seccion"]}',
                    'tipo_equipo': 'Máquina-herramienta',
                    'fabricante': 'Demo Manufacturer',
                    'año_fabricacion': random.randint(2015, 2022),
                }
            )
            equipos.append(equipo)
            if created:
                self.stdout.write(f'✅ Equipo creado: {equipo.codigo_interno}')
        
        # Crear planes de mantenimiento
        for equipo in equipos:
            plan, created = PlanMantenimiento.objects.get_or_create(
                equipo=equipo,
                defaults={
                    'nombre': f'Plan Preventivo {equipo.nombre}',
                    'tipo_mantenimiento': random.choice(['preventivo', 'predictivo']),
                    'frecuencia': random.choice(['mensual', 'trimestral', 'semestral']),
                    'duracion_estimada': random.uniform(2, 8),
                    'estado': 'activo',
                    'responsable_principal': user,
                    'fecha_inicio': date.today() - timedelta(days=random.randint(30, 365)),
                    'proxima_ejecucion': date.today() + timedelta(days=random.randint(1, 30)),
                    'prioridad': random.choice(['media', 'alta', 'critica']),
                    'costo_estimado': random.uniform(500, 2000),
                }
            )
            if created:
                self.stdout.write(f'✅ Plan creado: {plan.codigo_plan}')
        
        # Crear órdenes de trabajo históricas
        tipos_orden = ['preventivo', 'correctivo', 'predictivo', 'emergencia']
        estados = ['completada', 'completada', 'completada', 'en_progreso', 'pendiente']
        
        # Crear órdenes de los últimos 12 meses
        for i in range(50):
            fecha_base = datetime.now() - timedelta(days=random.randint(1, 365))
            equipo = random.choice(equipos)
            tipo = random.choice(tipos_orden)
            estado = random.choice(estados)
            
            # Más probabilidad de correctivos para equipos críticos
            if equipo.codigo_interno in ['TOR-001', 'SOL-001']:
                tipo = random.choice(['correctivo', 'correctivo', 'preventivo'])
            
            orden = OrdenTrabajo.objects.create(
                titulo=f'Mantenimiento {tipo} - {equipo.nombre}',
                descripcion=f'Trabajo de {tipo} realizado en {equipo.nombre}',
                equipo=equipo,
                tipo_orden=tipo,
                estado=estado,
                prioridad=random.choice(['normal', 'alta', 'urgente']),
                solicitante=user,
                asignado_a=user,
                fecha_creacion=fecha_base,
                fecha_programada=fecha_base + timedelta(hours=random.randint(1, 48)),
                horas_estimadas=random.uniform(1, 8),
                horas_reales=random.uniform(1, 10),
                costo_estimado=random.uniform(100, 1000),
                costo_real=random.uniform(100, 1200),
            )
            
            # Si está completada, agregar fecha de completación
            if estado == 'completada':
                orden.fecha_completada = orden.fecha_creacion + timedelta(
                    hours=float(orden.horas_reales)
                )
                orden.save()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'🎉 ¡Datos de demostración creados exitosamente!\n'
                f'📊 {len(equipos)} equipos\n'
                f'📋 {PlanMantenimiento.objects.count()} planes\n'
                f'🔧 {OrdenTrabajo.objects.count()} órdenes'
            )
        )