from django.core.management.base import BaseCommand
from apps.materiales.models import CategoriaMaterial

class Command(BaseCommand):
    help = 'Crea categorías predefinidas para herramientas'

    def handle(self, *args, **options):
        categorias_herramientas = [
            {
                'codigo': 'HM001',
                'nombre': 'Herramientas Manuales de Precisión',
                'tipo_categoria': 'herramientas_manuales',
                'descripcion': 'Llaves, destornilladores, alicates, martillos de precisión'
            },
            {
                'codigo': 'HM002',
                'nombre': 'Herramientas Manuales de Uso General',
                'tipo_categoria': 'herramientas_manuales',
                'descripcion': 'Herramientas básicas para trabajos generales'
            },
            {
                'codigo': 'HE001',
                'nombre': 'Herramientas Eléctricas Portátiles',
                'tipo_categoria': 'herramientas_electricas',
                'descripcion': 'Taladros, amoladoras, sierras eléctricas portátiles'
            },
            {
                'codigo': 'HE002',
                'nombre': 'Herramientas Eléctricas Estacionarias',
                'tipo_categoria': 'herramientas_electricas',
                'descripcion': 'Máquinas eléctricas fijas de taller'
            },
            {
                'codigo': 'IM001',
                'nombre': 'Instrumentos de Medición Digital',
                'tipo_categoria': 'instrumentos_medicion',
                'descripcion': 'Calibres digitales, micrómetros, comparadores'
            },
            {
                'codigo': 'IM002',
                'nombre': 'Instrumentos de Medición Analógica',
                'tipo_categoria': 'instrumentos_medicion',
                'descripcion': 'Instrumentos de medición tradicionales'
            },
            {
                'codigo': 'HP001',
                'nombre': 'Herramientas de Precisión Industrial',
                'tipo_categoria': 'herramientas_precision',
                'descripcion': 'Herramientas de alta precisión para manufactura'
            },
            {
                'codigo': 'HC001',
                'nombre': 'Herramientas de Corte Manual',
                'tipo_categoria': 'herramientas_corte',
                'descripcion': 'Sierras manuales, cuchillas, navajas especializadas'
            },
            {
                'codigo': 'HC002',
                'nombre': 'Herramientas de Corte Mecánico',
                'tipo_categoria': 'herramientas_corte',
                'descripcion': 'Fresas, brocas, machuelos, terrajas'
            },
            {
                'codigo': 'EL001',
                'nombre': 'Equipos de Laboratorio Básico',
                'tipo_categoria': 'equipos_laboratorio',
                'descripcion': 'Equipos básicos para análisis y pruebas'
            },
            {
                'codigo': 'EL002',
                'nombre': 'Equipos de Laboratorio Avanzado',
                'tipo_categoria': 'equipos_laboratorio',
                'descripcion': 'Equipos especializados de alta tecnología'
            },
            {
                'codigo': 'HS001',
                'nombre': 'Herramientas de Soldadura Manual',
                'tipo_categoria': 'herramientas_soldadura_eq',
                'descripcion': 'Electrodos, varillas, equipos de soldadura manual'
            },
            {
                'codigo': 'HN001',
                'nombre': 'Herramientas Neumáticas',
                'tipo_categoria': 'herramientas_neumaticas',
                'descripcion': 'Herramientas accionadas por aire comprimido'
            },
            {
                'codigo': 'HH001',
                'nombre': 'Herramientas Hidráulicas',
                'tipo_categoria': 'herramientas_hidraulicas',
                'descripcion': 'Herramientas accionadas hidráulicamente'
            },
            {
                'codigo': 'IC001',
                'nombre': 'Instrumentos de Calibración',
                'tipo_categoria': 'instrumentos_calibracion',
                'descripcion': 'Patrones y equipos para calibración'
            },
            {
                'codigo': 'HSE001',
                'nombre': 'Herramientas de Seguridad',
                'tipo_categoria': 'herramientas_seguridad',
                'descripcion': 'Herramientas especializadas en seguridad industrial'
            },
            {
                'codigo': 'HES001',
                'nombre': 'Herramientas Especializadas',
                'tipo_categoria': 'herramientas_especiales',
                'descripcion': 'Herramientas para aplicaciones específicas'
            },
        ]

        created_count = 0
        for cat_data in categorias_herramientas:
            categoria, created = CategoriaMaterial.objects.get_or_create(
                codigo=cat_data['codigo'],
                defaults=cat_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Creada categoría: {categoria.codigo} - {categoria.nombre}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Ya existe: {categoria.codigo} - {categoria.nombre}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\n✅ Proceso completado. Se crearon {created_count} nuevas categorías de herramientas.')
        )