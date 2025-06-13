from django.core.management.base import BaseCommand
from apps.capacitacion.models import CategoriaCapacitacion

class Command(BaseCommand):
    help = 'Crea categorías iniciales para cursos y talleres'

    def handle(self, *args, **options):
        categorias_iniciales = [
            {
                'nombre': 'Soldadura',
                'descripcion': 'Técnicas y procesos de soldadura industrial',
                'color_hex': '#ef4444',
                'icono': 'bi-fire',
                'orden': 1,
            },
            {
                'nombre': 'Maquinado',
                'descripcion': 'Operación de máquinas herramientas y técnicas de mecanizado',
                'color_hex': '#3b82f6',
                'icono': 'bi-gear',
                'orden': 2,
            },
            {
                'nombre': 'Seguridad Industrial',
                'descripcion': 'Normas y procedimientos de seguridad en el laboratorio',
                'color_hex': '#f59e0b',
                'icono': 'bi-shield-check',
                'orden': 3,
            },
            {
                'nombre': 'Mantenimiento',
                'descripcion': 'Mantenimiento preventivo y correctivo de equipos',
                'color_hex': '#10b981',
                'icono': 'bi-tools',
                'orden': 4,
            },
            {
                'nombre': 'Fundición',
                'descripcion': 'Procesos de fundición y moldeo de metales',
                'color_hex': '#8b5cf6',
                'icono': 'bi-droplet',
                'orden': 5,
            },
            {
                'nombre': 'Control de Calidad',
                'descripcion': 'Técnicas de inspección y control de calidad',
                'color_hex': '#06b6d4',
                'icono': 'bi-check-circle',
                'orden': 6,
            },
            {
                'nombre': 'Materiales',
                'descripcion': 'Propiedades y manejo de materiales industriales',
                'color_hex': '#84cc16',
                'icono': 'bi-layers',
                'orden': 7,
            },
            {
                'nombre': 'Automatización',
                'descripcion': 'Sistemas automatizados y control industrial',
                'color_hex': '#ec4899',
                'icono': 'bi-cpu',
                'orden': 8,
            },
        ]

        for categoria_data in categorias_iniciales:
            categoria, created = CategoriaCapacitacion.objects.get_or_create(
                nombre=categoria_data['nombre'],
                defaults=categoria_data
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Categoría "{categoria.nombre}" creada exitosamente')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️ Categoría "{categoria.nombre}" ya existe')
                )

        self.stdout.write(self.style.SUCCESS('🎉 Proceso completado'))