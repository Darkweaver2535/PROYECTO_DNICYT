import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PROYECTO_ACTIVOS_INDUSTRIALES.settings')
django.setup()

from apps.reportes.models import RegistroFalla
from apps.equipos.models import Equipo
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

def crear_fallas_ejemplo():
    """Crear fallas de ejemplo para el sistema"""
    
    # Obtener o crear equipos de ejemplo
    equipos_data = [
        {'codigo_interno': 'SLD-001', 'nombre': 'Soldadora MIG-220'},
        {'codigo_interno': 'TRN-003', 'nombre': 'Torno CNC-450'},
        {'codigo_interno': 'FRS-002', 'nombre': 'Fresadora Universal'},
        {'codigo_interno': 'CMP-001', 'nombre': 'Compresor de Aire'},
        {'codigo_interno': 'HRN-001', 'nombre': 'Horno de Fundición'},
    ]
    
    equipos = []
    for equipo_data in equipos_data:
        equipo, created = Equipo.objects.get_or_create(
            codigo_interno=equipo_data['codigo_interno'],
            defaults={
                'nombre': equipo_data['nombre'],
                'seccion': 'SOLDADURA',
                'estado': 'OPERATIVO',
                'ubicacion_fisica': 'Laboratorio Industrial',
                'tipo_equipo': 'Equipo Industrial'
            }
        )
        equipos.append(equipo)
        if created:
            print(f"✅ Equipo creado: {equipo.codigo_interno}")
    
    # Obtener o crear usuario administrador
    user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'first_name': 'Administrador',
            'last_name': 'Sistema',
            'email': 'admin@laboratorio.edu.bo',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        user.set_password('admin123')
        user.save()
        print(f"✅ Usuario admin creado")
    
    # Crear fallas de ejemplo
    fallas_data = [
        {
            'equipo': equipos[0],  # Soldadora
            'descripcion_falla': 'Sobrecalentamiento del transformador principal durante operación continua de más de 2 horas',
            'severidad': 'critica',
            'estado': 'analisis',
            'tipo_falla': 'electrica',
            'causa_raiz': 'falta_lubricacion',
            'tiempo_parada': 4.5,
            'causa_inmediata': 'Obstrucción del sistema de ventilación por acumulación de polvo metálico',
            'condiciones_operacion': 'Operación continua a máxima potencia por períodos prolongados',
            'supervisor': 'Ing. Carlos Rodriguez',
            'costo_reparacion': 1500.00,
            'fecha_ocurrencia': timezone.now() - timedelta(hours=2),
        },
        {
            'equipo': equipos[1],  # Torno
            'descripcion_falla': 'Desgaste prematuro del husillo principal, vibraciones excesivas detectadas durante mecanizado de precisión',
            'severidad': 'alta',
            'estado': 'solucionada',
            'tipo_falla': 'mecanica',
            'causa_raiz': 'falta_lubricacion',
            'tiempo_parada': 8.0,
            'causa_inmediata': 'Sistema de lubricación automática desconfigurado',
            'condiciones_operacion': 'Trabajo pesado continuo sin mantenimiento preventivo',
            'supervisor': 'Téc. María Gonzales',
            'costo_reparacion': 2800.00,
            'fecha_ocurrencia': timezone.now() - timedelta(days=1),
            'fecha_solucion': timezone.now() - timedelta(hours=6),
            'solucion_aplicada': 'Reemplazo de rodamientos del husillo y recalibración del sistema de lubricación',
            'tiempo_reparacion': 6.5,
        },
        {
            'equipo': equipos[2],  # Fresadora
            'descripcion_falla': 'Falla intermitente en el sistema de refrigeración del cabezal, temperatura elevada durante fresado',
            'severidad': 'media',
            'estado': 'identificada',
            'tipo_falla': 'hidraulica',
            'causa_raiz': 'componente_defectuoso',
            'tiempo_parada': 2.0,
            'causa_inmediata': 'Bomba de refrigeración presenta cavitación',
            'condiciones_operacion': 'Operación normal con refrigerante de baja calidad',
            'supervisor': 'Ing. Ana Vargas',
            'costo_reparacion': 850.00,
            'fecha_ocurrencia': timezone.now() - timedelta(days=3),
        },
        {
            'equipo': equipos[3],  # Compresor
            'descripcion_falla': 'Caída gradual de presión en el sistema de aire comprimido, no alcanza presión de trabajo',
            'severidad': 'baja',
            'estado': 'pendiente',
            'tipo_falla': 'neumatica',
            'causa_raiz': 'mantenimiento_inadecuado',
            'tiempo_parada': 0.5,
            'causa_inmediata': 'Filtros de aire obstruidos y válvulas desajustadas',
            'condiciones_operacion': 'Uso intermitente en ambiente con alta concentración de polvo',
            'supervisor': 'Téc. Luis Morales',
            'costo_reparacion': 320.00,
            'fecha_ocurrencia': timezone.now() - timedelta(days=5),
        },
        {
            'equipo': equipos[4],  # Horno
            'descripcion_falla': 'Fluctuaciones de temperatura fuera de los parámetros establecidos para fundición de aleaciones',
            'severidad': 'alta',
            'estado': 'analisis',
            'tipo_falla': 'temperatura',
            'causa_raiz': 'defecto_fabricacion',
            'tiempo_parada': 12.0,
            'causa_inmediata': 'Sensor de temperatura descalibrado y controlador PID defectuoso',
            'condiciones_operacion': 'Trabajo a alta temperatura (1200°C) con ciclos frecuentes',
            'supervisor': 'Ing. Pedro Mamani',
            'costo_reparacion': 3200.00,
            'fecha_ocurrencia': timezone.now() - timedelta(hours=6),
        },
    ]
    
    # Crear las fallas
    for i, falla_data in enumerate(fallas_data, 1):
        codigo_falla = f"FLL-{i:04d}"
        
        # Verificar si ya existe
        if not RegistroFalla.objects.filter(codigo_falla=codigo_falla).exists():
            falla = RegistroFalla.objects.create(
                codigo_falla=codigo_falla,
                reportado_por=user,
                asignado_a=user if falla_data['estado'] in ['analisis', 'solucionada'] else None,
                **{k: v for k, v in falla_data.items() if k not in ['fecha_solucion', 'solucion_aplicada', 'tiempo_reparacion']}
            )
            
            # Agregar campos adicionales si existen
            if 'fecha_solucion' in falla_data:
                falla.fecha_solucion = falla_data['fecha_solucion']
            if 'solucion_aplicada' in falla_data:
                falla.solucion_aplicada = falla_data['solucion_aplicada']
            if 'tiempo_reparacion' in falla_data:
                falla.tiempo_reparacion = falla_data['tiempo_reparacion']
            
            falla.save()
            print(f"✅ Falla creada: {falla.codigo_falla} - {falla.equipo.nombre}")
        else:
            print(f"⚠️  Falla ya existe: {codigo_falla}")

if __name__ == "__main__":
    crear_fallas_ejemplo()
    print("\n🎉 Datos de ejemplo creados exitosamente!")
    print("\n📋 Resumen:")
    print(f"   • Equipos: {Equipo.objects.count()}")
    print(f"   • Fallas: {RegistroFalla.objects.count()}")
    print(f"   • Usuarios: {User.objects.count()}")