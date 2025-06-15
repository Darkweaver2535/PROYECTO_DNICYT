from django.core.management.base import BaseCommand
from apps.normativas.models import CategoriaSeguridad

class Command(BaseCommand):
    help = 'Crea las categorías de seguridad por defecto para el sistema'

    def handle(self, *args, **options):
        categorias = [
            {
                'nombre': 'Seguridad en Soldadura',
                'descripcion': 'Normativas y protocolos de seguridad para procesos de soldadura',
                'color_hex': '#ef4444',
                'icono': 'bi-fire',
                'orden': 1,
                'es_critica': True
            },
            {
                'nombre': 'Seguridad en Maquinado',
                'descripcion': 'Protocolos de seguridad para operaciones de maquinado y torno',
                'color_hex': '#f59e0b',
                'icono': 'bi-gear-wide-connected',
                'orden': 2,
                'es_critica': True
            },
            {
                'nombre': 'Equipos de Protección Personal',
                'descripcion': 'Normativas sobre uso y mantenimiento de EPP',
                'color_hex': '#10b981',
                'icono': 'bi-shield-check',
                'orden': 3,
                'es_critica': True
            },
            {
                'nombre': 'Manejo de Materiales Peligrosos',
                'descripcion': 'Protocolos para el manejo seguro de sustancias químicas y materiales peligrosos',
                'color_hex': '#dc2626',
                'icono': 'bi-exclamation-triangle',
                'orden': 4,
                'es_critica': True
            },
            {
                'nombre': 'Emergencias y Evacuación',
                'descripcion': 'Procedimientos de emergencia, evacuación y primeros auxilios',
                'color_hex': '#7c2d12',
                'icono': 'bi-heart-pulse',
                'orden': 5,
                'es_critica': True
            },
            {
                'nombre': 'Seguridad Eléctrica',
                'descripcion': 'Normativas de seguridad para trabajos con electricidad',
                'color_hex': '#fbbf24',
                'icono': 'bi-lightning-charge',
                'orden': 6,
                'es_critica': True
            },
            {
                'nombre': 'Prevención de Incendios',
                'descripcion': 'Protocolos de prevención y combate de incendios',
                'color_hex': '#dc2626',
                'icono': 'bi-fire',
                'orden': 7,
                'es_critica': True
            },
            {
                'nombre': 'Seguridad en Fundición',
                'descripcion': 'Protocolos específicos para operaciones de fundición de metales',
                'color_hex': '#f97316',
                'icono': 'bi-droplet',
                'orden': 8,
                'es_critica': True
            },
            {
                'nombre': 'Ergonomía y Salud Ocupacional',
                'descripcion': 'Normativas sobre ergonomía y prevención de lesiones laborales',
                'color_hex': '#06b6d4',
                'icono': 'bi-person-arms-up',
                'orden': 9,
                'es_critica': False
            },
            {
                'nombre': 'Mantenimiento Seguro',
                'descripcion': 'Protocolos de seguridad para actividades de mantenimiento',
                'color_hex': '#8b5cf6',
                'icono': 'bi-tools',
                'orden': 10,
                'es_critica': False
            },
            {
                'nombre': 'Seguridad en Almacén',
                'descripcion': 'Normativas para el manejo seguro de inventarios y almacenamiento',
                'color_hex': '#84cc16',
                'icono': 'bi-box-seam',
                'orden': 11,
                'es_critica': False
            },
            {
                'nombre': 'Protocolos de Limpieza',
                'descripcion': 'Procedimientos de limpieza y descontaminación',
                'color_hex': '#06b6d4',
                'icono': 'bi-droplet-half',
                'orden': 12,
                'es_critica': False
            },
            {
                'nombre': 'Capacitación y Entrenamiento',
                'descripcion': 'Programas de capacitación en seguridad industrial',
                'color_hex': '#3b82f6',
                'icono': 'bi-mortarboard',
                'orden': 13,
                'es_critica': False
            },
            {
                'nombre': 'Auditorías de Seguridad',
                'descripcion': 'Procedimientos para auditorías y evaluaciones de seguridad',
                'color_hex': '#6366f1',
                'icono': 'bi-clipboard-check',
                'orden': 14,
                'es_critica': False
            },
            {
                'nombre': 'Normativas Generales',
                'descripcion': 'Políticas y normativas generales de seguridad del laboratorio',
                'color_hex': '#64748b',
                'icono': 'bi-file-earmark-text',
                'orden': 15,
                'es_critica': False
            }
        ]

        created_count = 0
        updated_count = 0

        for cat_data in categorias:
            categoria, created = CategoriaSeguridad.objects.get_or_create(
                nombre=cat_data['nombre'],
                defaults=cat_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Creada: {categoria.nombre}')
                )
            else:
                # Actualizar datos si ya existe
                for key, value in cat_data.items():
                    if key != 'nombre':  # No actualizar el nombre
                        setattr(categoria, key, value)
                categoria.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'↻ Actualizada: {categoria.nombre}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Proceso completado:'
                f'\n   - {created_count} categorías creadas'
                f'\n   - {updated_count} categorías actualizadas'
                f'\n   - Total de categorías: {CategoriaSeguridad.objects.count()}'
            )
        )